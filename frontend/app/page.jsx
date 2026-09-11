"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import api from "@/lib/api";

export default function Home() {
  const [mode, setMode] = useState("login"); // "login" | "register"
  const [form, setForm] = useState({ full_name: "", email: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const router = useRouter();

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const res = mode === "login"
        ? await api.login({ email: form.email, password: form.password })
        : await api.register(form);
      login(res);
      router.push("/dashboard");
    } catch (err) {
      setError(err?.response?.data?.detail || "Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto mt-8">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-slate-900">AI-Powered Adaptive Learning</h1>
        <p className="text-slate-500 mt-2">
          Quizzes, explanations, and difficulty adjust to you — automatically.
        </p>
      </div>

      <div className="card">
        <div className="flex mb-6 rounded-lg bg-slate-100 p-1">
          <button
            className={`flex-1 py-2 rounded-md text-sm font-medium transition-colors ${mode === "login" ? "bg-white shadow-sm text-brand-600" : "text-slate-500"}`}
            onClick={() => setMode("login")}
          >
            Sign in
          </button>
          <button
            className={`flex-1 py-2 rounded-md text-sm font-medium transition-colors ${mode === "register" ? "bg-white shadow-sm text-brand-600" : "text-slate-500"}`}
            onClick={() => setMode("register")}
          >
            Create account
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {mode === "register" && (
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Full name</label>
              <input
                name="full_name" required value={form.full_name} onChange={handleChange}
                className="w-full border border-slate-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-brand-400"
              />
            </div>
          )}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Email</label>
            <input
              type="email" name="email" required value={form.email} onChange={handleChange}
              className="w-full border border-slate-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-brand-400"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Password</label>
            <input
              type="password" name="password" required value={form.password} onChange={handleChange}
              className="w-full border border-slate-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-brand-400"
            />
          </div>

          {error && <p className="text-sm text-rose-600">{error}</p>}

          <button type="submit" disabled={loading} className="btn-primary w-full">
            {loading ? "Please wait…" : mode === "login" ? "Sign in" : "Create account"}
          </button>
        </form>

        <p className="text-xs text-slate-400 mt-4 text-center">
          Demo login (after running the seed script): demo@student.com / demo1234
        </p>
      </div>
    </div>
  );
}
