import { Link } from "react-router-dom";
import { useAuth, getRoleStorageKey } from "../contexts/AuthContext";
import { useState, useEffect } from "react";
import { getDocuments } from "../api/documentsAPI";

function readChatStats(role) {
  try {
    const key = getRoleStorageKey(role, "recents");
    const raw = localStorage.getItem(key);
    const recents = raw ? JSON.parse(raw) : [];
    if (!Array.isArray(recents)) return { conversations: 0, totalMessages: 0, recents: [] };

    // Đếm tổng messages từ tất cả conversations trong localStorage
    let totalMessages = 0;
    for (const r of recents) {
      const msgKey = getRoleStorageKey(role, `msgs_${r.id}`);
      const msgRaw = localStorage.getItem(msgKey);
      if (msgRaw) {
        try { totalMessages += JSON.parse(msgRaw) || 0; } catch {}
      }
    }

    return {
      conversations: recents.length,
      totalMessages,
      recents: [...recents].sort((a, b) => new Date(b.updatedAt || 0) - new Date(a.updatedAt || 0)),
    };
  } catch { return { conversations: 0, totalMessages: 0, recents: [] }; }
}

/* ── Admin Dashboard ── */
function AdminDashboard({ role, username, time, docStats, chatStats }) {
  const greeting = getGreeting(time);
  const timeStr = time.toLocaleTimeString("vi-VN", { hour: "2-digit", minute: "2-digit", second: "2-digit" });
  const dateStr = time.toLocaleDateString("vi-VN", { weekday: "long", day: "numeric", month: "long", year: "numeric" });

  const fmt = (n, loading) => {
    if (loading) return <span className="stat-loading">…</span>;
    if (n === null) return <span className="stat-na">—</span>;
    return n;
  };

  return (
    <div className="page">
      <div className="dash-hero">
        <div className="dash-hero-left">
          <div className="dash-role-badge" data-role="admin">🛡️ Admin</div>
          <h1 className="dash-greeting">{greeting}, {username}!</h1>
          <p className="dash-subline">Bạn có toàn quyền quản lý hệ thống FlowAssist RAG.</p>
        </div>
        <div className="dash-clock">
          <div className="clock-time">{timeStr}</div>
          <div className="clock-date">{dateStr}</div>
        </div>
      </div>

      <div className="dash-stats">
        {[
          { label: "Tài liệu đã upload", value: fmt(docStats.total, docStats.loading),    icon: "📄", color: "var(--blue)" },
          { label: "Đã ingest vào RAG",  value: fmt(docStats.ingested, docStats.loading), icon: "🧠", color: "var(--green)" },
          { label: "Conversations",      value: fmt(chatStats.conversations, false),       icon: "💬", color: "var(--purple)" },
        ].map((s, i) => (
          <div className="stat-card" key={i}>
            <div className="stat-icon" style={{ background: s.color + "18", color: s.color }}>{s.icon}</div>
            <div className="stat-value">{s.value}</div>
            <div className="stat-label">{s.label}</div>
          </div>
        ))}
      </div>

      <div className="dash-section-title">Hành động nhanh</div>
      <div className="dash-quick">
        {[
          { title: "Upload tài liệu",   desc: "Thêm tài liệu mới vào knowledge base", icon: "⬆️", to: "/documents", color: "var(--blue)" },
          { title: "Chat với AI",       desc: "Kiểm tra bot với tư cách admin",        icon: "🤖", to: "/chat",      color: "var(--purple)" },
          { title: "Quản lý Documents", desc: "Xem và ingest lại tài liệu hiện có",   icon: "📚", to: "/documents", color: "var(--green)" },
        ].map((q) => (
          <Link to={q.to} key={q.title} className="quick-card" style={{ "--qc": q.color }}>
            <div className="quick-icon">{q.icon}</div>
            <div className="quick-body">
              <div className="quick-title">{q.title}</div>
              <div className="quick-desc">{q.desc}</div>
            </div>
            <div className="quick-arrow">→</div>
          </Link>
        ))}
      </div>

      <div className="dash-bottom">
        <div className="card dash-activity">
          <div className="card-head" style={{ display: "flex", justifyContent: "space-between" }}>
            <span>💬 Conversations gần đây</span>
            <Link to="/chat" style={{ fontSize: 12, color: "var(--blue)", fontWeight: 600 }}>Xem tất cả →</Link>
          </div>
          <div className="activity-list">
            {chatStats.recents.length === 0 ? (
              <div className="empty">Chưa có hội thoại nào. <Link to="/chat" style={{ color: "var(--blue)" }}>Bắt đầu chat →</Link></div>
            ) : chatStats.recents.slice(0, 5).map((r, i) => (
              <div className="activity-item" key={i}>
                <div className="act-dot" style={{ background: "var(--blue)18", color: "var(--blue)", fontSize: 14 }}>💬</div>
                <div className="act-text">{r.title || "New conversation"}</div>
                <div className="act-time">{r.updatedAt ? new Date(r.updatedAt).toLocaleDateString("vi-VN") : ""}</div>
              </div>
            ))}
          </div>
        </div>

        <div className="card dash-system">
          <div className="card-head"><span>⚙️ Trạng thái hệ thống</span></div>
          <div className="system-list">
            {[
              { name: "API Server",    status: "online", color: "var(--green)" },
              { name: "RAG Engine",    status: "online", color: "var(--green)" },
              { name: "MinIO Storage", status: "online", color: "var(--green)" },
              { name: "Vector DB",     status: "online", color: "var(--green)" },
            ].map((s) => (
              <div className="system-item" key={s.name}>
                <div className="sys-name">{s.name}</div>
                <div className="sys-badge" style={{ background: s.color + "20", color: s.color }}>
                  <span className="sys-dot" style={{ background: s.color }} />{s.status}
                </div>
              </div>
            ))}
            <div className="system-item" style={{ marginTop: 8, paddingTop: 8, borderTop: "1px solid var(--border)" }}>
              <div className="sys-name">Documents</div>
              <div className="sys-badge" style={{ background: "var(--blue)18", color: "var(--blue)" }}>
                {docStats.loading ? "…" : docStats.error ? "lỗi API" : `${docStats.total} files`}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

/* ── User Dashboard ── */
function UserDashboard({ role, username, time, chatStats }) {
  const greeting = getGreeting(time);
  const timeStr = time.toLocaleTimeString("vi-VN", { hour: "2-digit", minute: "2-digit", second: "2-digit" });
  const dateStr = time.toLocaleDateString("vi-VN", { weekday: "long", day: "numeric", month: "long", year: "numeric" });

  const hasConvs = chatStats.conversations > 0;
  const latest = chatStats.recents[0] || null;

  return (
    <div className="page">
      {/* Hero */}
      <div className="dash-hero user-hero">
        <div className="dash-hero-left">
          <div className="dash-role-badge" data-role="user">👤 User</div>
          <h1 className="dash-greeting">{greeting}, {username}!</h1>
          <p className="dash-subline">FlowAssist sẵn sàng trả lời mọi câu hỏi của bạn.</p>
        </div>
        <div className="dash-clock">
          <div className="clock-time">{timeStr}</div>
          <div className="clock-date">{dateStr}</div>
        </div>
      </div>

      {/* CTA nếu chưa chat lần nào */}
      {!hasConvs && (
        <div className="user-cta-banner">
          <div className="user-cta-left">
            <div className="user-cta-icon">✨</div>
            <div>
              <div className="user-cta-title">Bắt đầu cuộc trò chuyện đầu tiên!</div>
              <div className="user-cta-sub">Hỏi bất kỳ điều gì — FlowAssist sẽ tra cứu knowledge base và trả lời cho bạn.</div>
            </div>
          </div>
          <Link to="/chat" className="user-cta-btn">Chat ngay →</Link>
        </div>
      )}

      {/* Stats */}
      <div className="dash-stats" style={{ gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))" }}>
        {[
          { label: "Conversations", value: chatStats.conversations, icon: "💬", color: "var(--blue)", to: "/chat" },
          { label: "Hội thoại hôm nay", value: chatStats.recents.filter(r => {
              const d = new Date(r.updatedAt||0); const today = new Date(); today.setHours(0,0,0,0); return d >= today;
            }).length, icon: "📅", color: "var(--purple)", to: "/chat" },
        ].map((s, i) => (
          <Link to={s.to} key={i} className="stat-card stat-card--link">
            <div className="stat-icon" style={{ background: s.color + "18", color: s.color }}>{s.icon}</div>
            <div className="stat-value">{s.value}</div>
            <div className="stat-label">{s.label}</div>
          </Link>
        ))}

        {/* Latest conversation card */}
        {latest && (
          <Link to="/chat" className="stat-card stat-card--link stat-card--latest">
            <div className="stat-icon" style={{ background: "var(--amber)18", color: "var(--amber)" }}>🕐</div>
            <div className="stat-value" style={{ fontSize: 13, fontWeight: 700, letterSpacing: 0, lineHeight: 1.4, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
              {latest.title || "New conversation"}
            </div>
            <div className="stat-label">Gần nhất</div>
          </Link>
        )}
      </div>

      {/* 2 cột chính */}
      <div className="user-main-grid">
        {/* Tiếp tục chat */}
        <div className="card user-continue-card">
          <div className="card-head" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <span>💬 Hội thoại gần đây</span>
            <Link to="/chat" className="card-link">Xem tất cả →</Link>
          </div>

          {!hasConvs ? (
            <div className="user-empty-convs">
              <div style={{ fontSize: 36 }}>🗨️</div>
              <div style={{ fontWeight: 600, marginTop: 10, color: "var(--text)" }}>Chưa có hội thoại nào</div>
              <div style={{ fontSize: 13, color: "var(--text-muted)", marginTop: 4 }}>Nhấn Chat để bắt đầu</div>
              <Link to="/chat" className="button" style={{ marginTop: 14, display: "inline-block" }}>Bắt đầu chat</Link>
            </div>
          ) : (
            <div className="user-conv-list">
              {chatStats.recents.slice(0, 6).map((r, i) => {
                const d = new Date(r.updatedAt || 0);
                const isToday = d >= (() => { const t = new Date(); t.setHours(0,0,0,0); return t; })();
                return (
                  <Link to="/chat" key={i} className="user-conv-item">
                    <div className="user-conv-avatar">💬</div>
                    <div className="user-conv-body">
                      <div className="user-conv-title">{r.title || "New conversation"}</div>
                      <div className="user-conv-time">
                        {isToday
                          ? `Hôm nay ${d.toLocaleTimeString("vi-VN", { hour: "2-digit", minute: "2-digit" })}`
                          : d.toLocaleDateString("vi-VN", { day: "numeric", month: "short" })}
                      </div>
                    </div>
                    <div className="user-conv-arrow">→</div>
                  </Link>
                );
              })}
            </div>
          )}
        </div>

        {/* Panel phải */}
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          {/* New chat CTA */}
          <Link to="/chat" className="user-new-chat-card">
            <div className="user-new-chat-icon">✏️</div>
            <div>
              <div className="user-new-chat-title">Cuộc trò chuyện mới</div>
              <div className="user-new-chat-sub">Bắt đầu một chat mới với FlowAssist</div>
            </div>
            <div className="user-conv-arrow" style={{ marginLeft: "auto" }}>→</div>
          </Link>

          {/* Tips card */}
          <div className="card user-tips-card">
            <div className="card-head">💡 Mẹo sử dụng</div>
            <div className="user-tips-list">
              {[
                { icon: "🔍", tip: "Hỏi chi tiết để nhận câu trả lời chính xác hơn" },
                { icon: "📎", tip: "Có thể hỏi về nội dung trong tài liệu đã upload" },
                { icon: "↩️", tip: "Enter để gửi, Shift+Enter để xuống dòng" },
                { icon: "🗂️", tip: "Tiêu đề hội thoại tự đặt từ câu hỏi đầu tiên" },
              ].map((t, i) => (
                <div className="user-tip-item" key={i}>
                  <span className="user-tip-icon">{t.icon}</span>
                  <span className="user-tip-text">{t.tip}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function getGreeting(time) {
  const h = time.getHours();
  if (h < 12) return "Chào buổi sáng";
  if (h < 18) return "Chào buổi chiều";
  return "Chào buổi tối";
}

export default function DashboardPage() {
  const { role, username, isAdmin } = useAuth();
  const [time, setTime] = useState(new Date());
  const [docStats, setDocStats] = useState({ total: null, ingested: null, loading: true, error: false });
  const [chatStats, setChatStats] = useState({ conversations: 0, totalMessages: 0, recents: [] });

  useEffect(() => {
    const t = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(t);
  }, []);

  useEffect(() => {
    const update = () => setChatStats(readChatStats(role));
    update();
    window.addEventListener("storage", update);
    const poll = setInterval(update, 2000);
    return () => { window.removeEventListener("storage", update); clearInterval(poll); };
  }, [role]);

  useEffect(() => {
    if (!isAdmin) { setDocStats({ total: null, ingested: null, loading: false, error: false }); return; }
    (async () => {
      try {
        const docs = await getDocuments();
        const total = Array.isArray(docs) ? docs.length : 0;
        const ingested = Array.isArray(docs) ? docs.filter(d => d.doc_metadata?.status === "ingested").length : 0;
        setDocStats({ total, ingested, loading: false, error: false });
      } catch {
        setDocStats({ total: null, ingested: null, loading: false, error: true });
      }
    })();
  }, [isAdmin]);

  if (isAdmin) {
    return <AdminDashboard role={role} username={username} time={time} docStats={docStats} chatStats={chatStats} />;
  }
  return <UserDashboard role={role} username={username} time={time} chatStats={chatStats} />;
}