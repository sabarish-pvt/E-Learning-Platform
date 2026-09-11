"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/AuthContext";

export default function Navbar() {
  const { student, logout } = useAuth();
  const router = useRouter();

  const handleLogout = () => {
    logout();
    router.push("/");
  };

  return (
    <nav className="bg-white border-b border-slate-200 sticky top-0 z-10">
      <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
        <Link href="/" className="font-bold text-lg text-brand-600">
          Adaptive<span className="text-slate-800">Learn</span>
        </Link>

        {student ? (
          <div className="flex items-center gap-6 text-sm">
            <Link href="/dashboard" className="text-slate-600 hover:text-brand-600">Dashboard</Link>
            <Link href="/courses" className="text-slate-600 hover:text-brand-600">Courses</Link>
            <span className="text-slate-500">Hi, {student.full_name.split(" ")[0]}</span>
            <button onClick={handleLogout} className="btn-secondary py-1.5">Log out</button>
          </div>
        ) : (
          <Link href="/" className="btn-primary py-1.5">Sign in</Link>
        )}
      </div>
    </nav>
  );
}
