"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import api from "@/lib/api";

export default function CourseDetailPage() {
  const { id } = useParams();
  const router = useRouter();
  const { student } = useAuth();
  const [course, setCourse] = useState(null);

  useEffect(() => {
    api.getCourse(id).then(setCourse);
  }, [id]);

  if (!course) return <p className="text-slate-500">Loading course…</p>;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">{course.title}</h1>
        <p className="text-slate-500 mt-1">{course.description}</p>
      </div>

      <div className="card">
        <h2 className="font-semibold text-slate-800 mb-4">Topics</h2>
        <ul className="divide-y divide-slate-100">
          {course.topics.map((topic) => (
            <li key={topic.id} className="py-3 flex items-center justify-between">
              <div>
                <p className="font-medium text-slate-800">{topic.title}</p>
                <p className="text-sm text-slate-500">{topic.summary}</p>
              </div>
              <button
                onClick={() => router.push(`/topics/${topic.id}`)}
                className="btn-secondary text-sm"
                disabled={!student}
                title={!student ? "Sign in to view this topic" : ""}
              >
                Open
              </button>
            </li>
          ))}
          {course.topics.length === 0 && <p className="text-slate-500 text-sm py-2">No topics added yet.</p>}
        </ul>
      </div>
    </div>
  );
}
