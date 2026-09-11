"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import DifficultyBadge from "@/components/DifficultyBadge";
import ProgressChart from "@/components/ProgressChart";
import api from "@/lib/api";

export default function Dashboard() {
  const { student, loaded, updateStudent } = useAuth();
  const router = useRouter();
  const [summary, setSummary] = useState(null);
  const [progress, setProgress] = useState([]);
  const [topicNames, setTopicNames] = useState({});
  const [recommending, setRecommending] = useState(false);

  useEffect(() => {
    if (loaded && !student) router.push("/");
  }, [loaded, student, router]);

  useEffect(() => {
    if (!student) return;
    (async () => {
      const [summaryData, progressData, courses] = await Promise.all([
        api.getProgressSummary(student.id),
        api.getProgress(student.id),
        api.listCourses(),
      ]);
      setSummary(summaryData);
      setProgress(progressData);

      const names = {};
      courses.forEach((c) => c.topics.forEach((t) => (names[t.id] = t.title)));
      setTopicNames(names);
    })();
  }, [student]);

  const handleRecommend = async () => {
    setRecommending(true);
    try {
      const rec = await api.recommendDifficulty(student.id);
      const refreshed = await api.getStudent(student.id);
      updateStudent(refreshed);
      setSummary((prev) => ({ ...prev, current_difficulty: rec.recommended_difficulty }));
    } finally {
      setRecommending(false);
    }
  };

  if (!student || !summary) {
    return <p className="text-slate-500">Loading your dashboard…</p>;
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Welcome back, {student.full_name.split(" ")[0]}</h1>
        <p className="text-slate-500">Here's how your learning is adapting to you.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatCard label="Average score" value={`${summary.avg_score}%`} />
        <StatCard label="Quizzes taken" value={summary.quizzes_taken} />
        <StatCard label="Current streak" value={summary.current_streak} />
        <div className="card flex flex-col justify-between">
          <span className="text-sm text-slate-500">Recommended difficulty</span>
          <div className="mt-2 flex items-center justify-between">
            <DifficultyBadge level={summary.current_difficulty} />
            <button onClick={handleRecommend} disabled={recommending} className="text-xs text-brand-600 hover:underline">
              {recommending ? "Analyzing…" : "Re-analyze"}
            </button>
          </div>
        </div>
      </div>

      <div className="card">
        <h2 className="font-semibold text-slate-800 mb-4">Topic mastery</h2>
        <ProgressChart progressRecords={progress} topicNames={topicNames} />
      </div>

      <div className="card flex items-center justify-between">
        <div>
          <h2 className="font-semibold text-slate-800">Ready for more practice?</h2>
          <p className="text-sm text-slate-500">
            We'll generate a quiz at your current level: <DifficultyBadge level={summary.current_difficulty} />
          </p>
        </div>
        <button onClick={() => router.push("/courses")} className="btn-primary">Browse courses</button>
      </div>
    </div>
  );
}

function StatCard({ label, value }) {
  return (
    <div className="card">
      <span className="text-sm text-slate-500">{label}</span>
      <p className="text-2xl font-bold text-slate-900 mt-1">{value}</p>
    </div>
  );
}
