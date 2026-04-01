import { useState } from "react";
import { useAuth } from "../contexts/AuthContext";

export default function LoginPage() {
  const { login } = useAuth();
  const [hovered, setHovered] = useState(null);

  return (
    <div className="login-root">
      <div className="login-bg">
        <div className="login-orb orb1" />
        <div className="login-orb orb2" />
        <div className="login-grid-lines" />
      </div>

      <div className="login-card">
        <div className="login-logo">
          <span className="logo-icon">⚡</span>
          <span className="logo-text">FlowAssist</span>
        </div>
        <h1 className="login-title">Chào mừng trở lại</h1>
        <p className="login-sub">Chọn vai trò để tiếp tục</p>

        <div className="login-roles">
          <button
            className={`role-card ${hovered === "admin" ? "hov" : ""}`}
            onMouseEnter={() => setHovered("admin")}
            onMouseLeave={() => setHovered(null)}
            onClick={() => login("admin")}
          >
            <div className="role-icon admin-icon">🛡️</div>
            <div className="role-info">
              <div className="role-name">Admin</div>
              <div className="role-desc">Quản lý tài liệu, knowledge base và toàn bộ hệ thống</div>
            </div>
            <div className="role-arrow">→</div>
          </button>

          <button
            className={`role-card ${hovered === "user" ? "hov" : ""}`}
            onMouseEnter={() => setHovered("user")}
            onMouseLeave={() => setHovered(null)}
            onClick={() => login("user")}
          >
            <div className="role-icon user-icon">💬</div>
            <div className="role-info">
              <div className="role-name">User</div>
              <div className="role-desc">Chat với AI assistant và tra cứu knowledge base</div>
            </div>
            <div className="role-arrow">→</div>
          </button>
        </div>

        <div className="login-footer">Demo mode — không yêu cầu mật khẩu</div>
      </div>
    </div>
  );
}