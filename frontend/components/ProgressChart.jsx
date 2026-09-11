"use client";

import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";

export default function ProgressChart({ progressRecords, topicNames }) {
  if (!progressRecords || progressRecords.length === 0) {
    return <p className="text-slate-500 text-sm">No progress yet — start a quiz to see your mastery here.</p>;
  }

  const data = progressRecords.map((p) => ({
    name: topicNames[p.topic_id] || `Topic ${p.topic_id}`,
    mastery: p.mastery_percent,
  }));

  return (
    <ResponsiveContainer width="100%" height={260}>
      <BarChart data={data} margin={{ top: 10, right: 10, left: -10, bottom: 10 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
        <XAxis dataKey="name" tick={{ fontSize: 12 }} interval={0} angle={-15} textAnchor="end" height={60} />
        <YAxis domain={[0, 100]} tick={{ fontSize: 12 }} />
        <Tooltip formatter={(value) => [`${value}%`, "Mastery"]} />
        <Bar dataKey="mastery" fill="#3266d6" radius={[6, 6, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}
