import { createContext, useContext, useState } from "react";

const AuthContext = createContext(null);

// Mỗi role có namespace riêng trong localStorage
export function getRoleStorageKey(role, key) {
  return `fa_${role}_${key}`;
}

export function AuthProvider({ children }) {
  const [role, setRole] = useState(() => localStorage.getItem("fa_role") || null);
  const [username, setUsername] = useState(() => localStorage.getItem("fa_username") || "");

  const login = (selectedRole) => {
    const name = selectedRole === "admin" ? "Admin" : "User";
    setRole(selectedRole);
    setUsername(name);
    localStorage.setItem("fa_role", selectedRole);
    localStorage.setItem("fa_username", name);
  };

  const logout = () => {
    setRole(null);
    setUsername("");
    localStorage.removeItem("fa_role");
    localStorage.removeItem("fa_username");
  };

  return (
    <AuthContext.Provider value={{ role, username, login, logout, isAdmin: role === "admin" }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}