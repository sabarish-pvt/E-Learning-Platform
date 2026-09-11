"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import api from "@/lib/api";

export default function CoursesPage() {
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.listCourses().then((data) => {
      setCourses(data);
      setLoading(false);
    });
  }, []);

  if (loading) return <p className="text-slate-500">Loading courses…</p>;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-slate-900">Courses</h1>

      {courses.length === 0 ? (
        <p className="text-slate-500">
          No courses yet. Run <code className="bg-slate-100 px-1 rounded">python -m app.seed</code> in the
          backend, or create one via <code className="bg-slate-100 px-1 rounded">POST /courses</code>.
        </p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {courses.map((course) => (
            <Link key={course.id} href={`/courses/${course.id}`} className="card hover:shadow-md transition-shadow">
              <h2 className="font-semibold text-lg text-slate-900">{course.title}</h2>
              <p className="text-sm text-slate-500 mt-1">{course.description}</p>
              <div className="mt-3 flex items-center justify-between text-xs text-slate-400">
                <span>{course.subject}</span>
                <span>{course.topics.length} topics</span>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
