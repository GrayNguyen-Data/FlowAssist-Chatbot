import { NavLink, Route, Routes, Navigate, useLocation, useNavigate } from "react-router-dom";
import { useAuth, getRoleStorageKey } from "./contexts/AuthContext";
import { useState, useEffect } from "react";
import DashboardPage from "./pages/DashboardPage";
import ChatPage from "./pages/ChatPage";
import DocumentsPage from "./pages/DocumentsPage";
import LoginPage from "./pages/LoginPage";

const NAV_ITEMS_ADMIN = [
  { to: "/", label: "Dashboard", icon: "🏠", end: true },
  { to: "/chat", label: "Chat", icon: "💬" },
  { to: "/documents", label: "Documents", icon: "📚" },
];

const NAV_ITEMS_USER = [
  { to: "/", label: "Dashboard", icon: "🏠", end: true },
  { to: "/chat", label: "Chat", icon: "💬" },
];

function RecentConversations({ role }) {
  const [recents, setRecents] = useState([]);
  const location = useLocation();
  const navigate = useNavigate();

  const readRecents = () => {
    try {
      const key = getRoleStorageKey(role, "recents");
      const raw = localStorage.getItem(key);
      const p = raw ? JSON.parse(raw) : [];
      return Array.isArray(p)
        ? [...p].sort((a, b) => new Date(b.updatedAt || 0) - new Date(a.updatedAt || 0))
        : [];
    } catch { return []; }
  };

  useEffect(() => { setRecents(readRecents()); }, [role, location.pathname]);

  useEffect(() => {
    const onStorage = () => setRecents(readRecents());
    const poll = setInterval(() => setRecents(readRecents()), 1500);
    window.addEventListener("storage", onStorage);
    return () => { window.removeEventListener("storage", onStorage); clearInterval(poll); };
  }, [role]);

  const handleNewChat = () => {
    // Xóa active conversation để ChatPage tự tạo mới
    localStorage.removeItem(getRoleStorageKey(role, "active_id"));
    localStorage.removeItem(getRoleStorageKey(role, "active_title"));
    navigate("/chat");
  };

  return (
    <div className="sidebar-recents">
      {recents.length > 0 && (
        <>
          <div className="nav-section-label" style={{ paddingTop: 0 }}>Recents</div>
          <div className="sidebar-recents-list">
            {recents.slice(0, 8).map((item) => (
              <NavLink
                key={item.id}
                to="/chat"
                className="recents-nav-item"
                title={item.title}
              >
                <span className="recents-nav-icon">💬</span>
                <span className="recents-nav-name">{item.title || "New conversation"}</span>
              </NavLink>
            ))}
          </div>
        </>
      )}
    </div>
  );
}

function Sidebar() {
  const { role, username, isAdmin, logout } = useAuth();
  const items = isAdmin ? NAV_ITEMS_ADMIN : NAV_ITEMS_USER;

  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <span className="logo-mark">⚡</span>
        <span className="logo-name">FlowAssist</span>
      </div>

      <div className="sidebar-user">
        <div className="sidebar-avatar">{isAdmin ? "🛡️" : "👤"}</div>
        <div className="sidebar-user-info">
          <div className="sidebar-username">{username}</div>
          <div className={`sidebar-role-tag ${role}`}>{isAdmin ? "Admin" : "User"}</div>
        </div>
      </div>

      <nav className="sidebar-nav">
        <div className="nav-section-label">Menu</div>
        {items.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.end}
            className={({ isActive }) => `nav-link ${isActive ? "active" : ""}`}
          >
            <span className="nav-icon">{item.icon}</span>
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>

      <RecentConversations role={role} />

      <div className="sidebar-bottom">
        <button className="logout-btn" onClick={logout}>
          <span>🚪</span> Đăng xuất
        </button>
      </div>
    </aside>
  );
}

function ProtectedLayout() {
  const { isAdmin } = useAuth();
  return (
    <div className="app-shell">
      <Sidebar />
      <main className="app-main">
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/chat" element={<ChatPage />} />
          {isAdmin && <Route path="/documents" element={<DocumentsPage />} />}
          {!isAdmin && <Route path="/documents" element={<Navigate to="/" replace />} />}
        </Routes>
      </main>
    </div>
  );
}

export default function App() {
  const { role } = useAuth();
  if (!role) return <LoginPage />;
  return <ProtectedLayout />;
}