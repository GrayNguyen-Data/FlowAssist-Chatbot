import { useEffect, useMemo, useRef, useState } from "react";
import { createConversation, getConversationMessages, sendChatMessage } from "../api/chatAPI";
import { useAuth, getRoleStorageKey } from "../contexts/AuthContext";

function makeTitle(text) {
  const clean = (text || "").replace(/\s+/g, " ").trim();
  if (!clean) return "New conversation";
  return clean.length > 40 ? `${clean.slice(0, 40)}…` : clean;
}

function groupByDate(items) {
  const now = new Date();
  const today     = new Date(now); today.setHours(0,0,0,0);
  const yesterday = new Date(today); yesterday.setDate(today.getDate() - 1);
  const week      = new Date(today); week.setDate(today.getDate() - 7);
  const month     = new Date(today); month.setDate(today.getDate() - 30);

  const groups = { "Hôm nay": [], "Hôm qua": [], "7 ngày qua": [], "30 ngày qua": [], "Cũ hơn": [] };
  for (const item of items) {
    const d = new Date(item.updatedAt || 0); d.setHours(0,0,0,0);
    if (d >= today)          groups["Hôm nay"].push(item);
    else if (d >= yesterday) groups["Hôm qua"].push(item);
    else if (d >= week)      groups["7 ngày qua"].push(item);
    else if (d >= month)     groups["30 ngày qua"].push(item);
    else                     groups["Cũ hơn"].push(item);
  }
  return Object.entries(groups).filter(([, v]) => v.length > 0);
}

function MessageBubble({ role, content }) {
  return (
    <div className={`chat-bubble-row ${role === "error" ? "assistant" : role}`}>
      <div className={`chat-avatar ${role === "error" ? "error" : role}`}>
        {role === "user" ? "👤" : role === "error" ? "⚠️" : "🤖"}
      </div>
      <div className="chat-bubble-wrap">
        <div className={`chat-bubble ${role}`}>{content}</div>
      </div>
    </div>
  );
}

export default function ChatPage() {
  const { isAdmin, role } = useAuth();

  const RECENTS_KEY = getRoleStorageKey(role, "recents");
  const ACTIVE_KEY  = getRoleStorageKey(role, "active_id");
  const TITLE_KEY   = getRoleStorageKey(role, "active_title");

  const readRecents = () => {
    try {
      const raw = localStorage.getItem(RECENTS_KEY);
      const p = raw ? JSON.parse(raw) : [];
      return Array.isArray(p) ? [...p].sort((a,b) => new Date(b.updatedAt||0) - new Date(a.updatedAt||0)) : [];
    } catch { return []; }
  };
  const writeRecents = (items) => localStorage.setItem(RECENTS_KEY, JSON.stringify(items));
  const upsertRecent = (id, title) => {
    const next = [{ id, title, updatedAt: new Date().toISOString() }, ...readRecents().filter(r => r.id !== id)];
    writeRecents(next); return next;
  };
  const removeRecent = (id) => { const n = readRecents().filter(r => r.id !== id); writeRecents(n); return n; };

  const [convId, setConvId]       = useState("");
  const [convTitle, setConvTitle] = useState("New conversation");
  const [recents, setRecents]     = useState([]);
  const [messages, setMessages]   = useState([]);
  const [context, setContext]     = useState([]);
  const [input, setInput]         = useState("");
  const [loading, setLoading]     = useState(false);
  const [booting, setBooting]     = useState(true);
  const [bootErr, setBootErr]     = useState(null);
  const [showCtx, setShowCtx]     = useState(false);
  const endRef = useRef(null);

  const persist = (id, title) => {
    setConvId(id); setConvTitle(title);
    localStorage.setItem(ACTIVE_KEY, id);
    localStorage.setItem(TITLE_KEY, title);
  };

  const createNew = async (title = "New conversation") => {
    const res = await createConversation({ userId: role === "admin" ? "admin" : "default", title, channel: "chat" });
    const id = res.conversation_id;
    const t  = res.title || title;
    persist(id, t);
    setRecents(upsertRecent(id, t));
    setMessages([]); setContext([]);
    return id;
  };

  const loadConv = async (id, title) => {
    setLoading(true); setBootErr(null);
    try {
      const history = await getConversationMessages(id);
      setMessages(Array.isArray(history)
        ? history.map(m => ({ id: m.message_id, role: m.role, content: m.content }))
        : []);
      persist(id, title);
      setRecents(upsertRecent(id, title));
      setContext([]);
    } catch (e) {
      setBootErr(e.message);
      setRecents(removeRecent(id));
      if (localStorage.getItem(ACTIVE_KEY) === id) {
        localStorage.removeItem(ACTIVE_KEY);
        localStorage.removeItem(TITLE_KEY);
      }
    } finally { setLoading(false); }
  };

  useEffect(() => {
    (async () => {
      try {
        const r = readRecents(); setRecents(r);
        const savedId    = localStorage.getItem(ACTIVE_KEY);
        const savedTitle = localStorage.getItem(TITLE_KEY) || "New conversation";
        if (savedId)       await loadConv(savedId, savedTitle);
        else if (r.length) await loadConv(r[0].id, r[0].title);
        else               await createNew();
      } catch (e) { setBootErr(e.message); }
      finally { setBooting(false); }
    })();
  }, [role]);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const canSend = useMemo(() => !!input.trim() && !!convId && !loading, [input, convId, loading]);

  const handleNew = async () => {
    try { setLoading(true); await createNew(`Chat ${new Date().toLocaleTimeString()}`); }
    catch (e) { setBootErr(e.message); }
    finally { setLoading(false); }
  };

  const handleSelect = (item) => { if (item.id !== convId) loadConv(item.id, item.title); };

  const handleDelete = async (e, id) => {
    e.stopPropagation();
    const next = removeRecent(id); setRecents(next);
    if (id === convId) {
      setMessages([]); setContext([]);
      localStorage.removeItem(ACTIVE_KEY); localStorage.removeItem(TITLE_KEY);
      if (next.length) await loadConv(next[0].id, next[0].title);
      else { try { setLoading(true); await createNew(); } finally { setLoading(false); } }
    }
  };

  const handleSend = async () => {
    if (!canSend) return;
    const text = input.trim();
    const isFirst = messages.filter(m => m.role === "user").length === 0;
    const derived = isFirst ? makeTitle(text) : convTitle;
    setInput(""); setLoading(true);
    setMessages(p => [...p, { id: `u-${Date.now()}`, role: "user", content: text }]);
    try {
      if (isFirst) {
        setConvTitle(derived);
        localStorage.setItem(TITLE_KEY, derived);
        setRecents(upsertRecent(convId, derived));
      }
      const res = await sendChatMessage({ conversationId: convId, message: text });
      setMessages(p => [...p, { id: `a-${Date.now()}`, role: "assistant", content: res.assistant_message }]);
      setContext(res.retrieved_context || []);
    } catch (e) {
      setMessages(p => [...p, { id: `e-${Date.now()}`, role: "error", content: `⚠️ ${e.message || "Lỗi server"}` }]);
    } finally { setLoading(false); }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); handleSend(); }
  };

  if (booting) return (
    <div className="chat-boot">
      <div className="chat-boot-spinner"/>
      <p>Đang kết nối tới server...</p>
    </div>
  );

  if (bootErr && !convId) return (
    <div className="chat-boot">
      <div style={{ fontSize: 40 }}>⚠️</div>
      <p style={{ fontWeight: 700, fontSize: 16, margin: 0 }}>Không thể khởi động Chat</p>
      <p className="boot-error-msg">{bootErr}</p>
      <button className="button" onClick={() => { setBootErr(null); setBooting(true); }}>🔄 Thử lại</button>
    </div>
  );

  return (
    <div className="chat-shell">

      {/* ── Main chat area ── */}
      <div className="chat-main">
        <div className="chat-main-head">
          <span className={`chat-role-pill chat-role-pill--${role}`}>
            {isAdmin ? "🛡️ Admin" : "👤 User"}
          </span>
          <button className="btn-new-chat" onClick={handleNew} disabled={loading}>
            ✏️ New chat
          </button>
        </div>

        <div className="chat-messages">
          {messages.length === 0 ? (
            <div className="chat-empty">
              <div className="chat-empty-icon">🤖</div>
              <div className="chat-empty-text">Hãy bắt đầu cuộc trò chuyện!</div>
              <div className="chat-empty-sub">Tiêu đề sẽ tự lấy từ câu hỏi đầu tiên.</div>
            </div>
          ) : (
            messages.map(msg => <MessageBubble key={msg.id} role={msg.role} content={msg.content}/>)
          )}

          {loading && (
            <div className="chat-bubble-row assistant">
              <div className="chat-avatar assistant">🤖</div>
              <div className="chat-bubble-wrap">
                <div className="chat-bubble assistant typing">
                  <span className="dot"/><span className="dot"/><span className="dot"/>
                </div>
              </div>
            </div>
          )}
          <div ref={endRef}/>
        </div>

        <div className="chat-input-area">
          <textarea
            className="chat-input"
            placeholder="Nhập câu hỏi... (Enter gửi, Shift+Enter xuống dòng)"
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            rows={1}
          />
          <button className="chat-send-btn" onClick={handleSend} disabled={!canSend}>↑</button>
        </div>
      </div>

      {/* ── Context panel (admin only) ── */}
      {isAdmin && showCtx && (
        <div className="chat-context-panel">
          <div className="ctx-panel-head">🔍 Retrieved Context</div>
          {context.length === 0
            ? <div className="ctx-empty">Gửi tin nhắn để xem context.</div>
            : context.map((c, i) => (
              <div className="ctx-item" key={i}>
                <div className="ctx-num">#{i+1}</div>
                <div className="ctx-text">{c}</div>
              </div>
            ))
          }
        </div>
      )}
    </div>
  );
}