"use client";

import { createContext, useContext, useEffect, useState } from "react";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [student, setStudent] = useState(null);
  const [token, setToken] = useState(null);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    const savedStudent = localStorage.getItem("student");
    const savedToken = localStorage.getItem("token");
    if (savedStudent && savedToken) {
      setStudent(JSON.parse(savedStudent));
      setToken(savedToken);
    }
    setLoaded(true);
  }, []);

  const login = (authResponse) => {
    setStudent(authResponse.student);
    setToken(authResponse.access_token);
    localStorage.setItem("student", JSON.stringify(authResponse.student));
    localStorage.setItem("token", authResponse.access_token);
  };

  const updateStudent = (updated) => {
    setStudent(updated);
    localStorage.setItem("student", JSON.stringify(updated));
  };

  const logout = () => {
    setStudent(null);
    setToken(null);
    localStorage.removeItem("student");
    localStorage.removeItem("token");
  };

  return (
    <AuthContext.Provider value={{ student, token, loaded, login, logout, updateStudent }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
