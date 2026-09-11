"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import DifficultyBadge from "@/components/DifficultyBadge";
import api from "@/lib/api";

export default function TopicDetailPage() {
  const { id } = useParams();
  const router = useRouter();
  const { student } = useAuth();

  const [topic, setTopic] = useState(null);
  const [materials, setMaterials] = useState([]);
  const [notes, setNotes] = useState(null);
  const [notesLoading, setNotesLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [uploadTitle, setUploadTitle] = useState("");
  const [uploadFile, setUploadFile] = useState(null);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    if (!student) {
      router.push("/");
      return;
    }
    api.getTopic(id).then(setTopic);
    api.getTopicMaterials(id).then(setMaterials);
  }, [id, student]);

  const handleGetNotes = async () => {
    setNotesLoading(true);
    try {
      const data = await api.getPracticeNotes(id, student.current_difficulty);
      setNotes(data.notes_markdown);
    } finally {
      setNotesLoading(false);
    }
  };

  const handleStartQuiz = async () => {
    setGenerating(true);
    try {
      const quiz = await api.generateQuizForStudent(student.id, Number(id), 5);
      router.push(`/quiz/${quiz.id}`);
    } finally {
      setGenerating(false);
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!uploadFile || !uploadTitle) return;
    setUploading(true);
    try {
      const formData = new FormData();
      formData.append("topic_id", id);
      formData.append("title", uploadTitle);
      formData.append("file", uploadFile);
      const material = await api.uploadMaterial(formData);
      setMaterials((prev) => [...prev, material]);
      setUploadTitle("");
      setUploadFile(null);
    } catch (err) {
      alert(err?.response?.data?.detail || "Upload failed. Check your Cloudinary credentials.");
    } finally {
      setUploading(false);
    }
  };

  if (!topic) return <p className="text-slate-500">Loading topic…</p>;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">{topic.title}</h1>
        <p className="text-slate-500 mt-1">{topic.summary}</p>
      </div>

      <div className="card flex items-center justify-between">
        <div>
          <h2 className="font-semibold text-slate-800">Adaptive quiz</h2>
          <p className="text-sm text-slate-500 flex items-center gap-2 mt-1">
            Generated at your recommended level: <DifficultyBadge level={student?.current_difficulty} />
          </p>
        </div>
        <button onClick={handleStartQuiz} disabled={generating} className="btn-primary">
          {generating ? "Generating…" : "Start quiz"}
        </button>
      </div>

      <div className="card">
        <div className="flex items-center justify-between mb-3">
          <h2 className="font-semibold text-slate-800">AI study notes</h2>
          <button onClick={handleGetNotes} disabled={notesLoading} className="btn-secondary text-sm">
            {notesLoading ? "Generating…" : "Generate notes"}
          </button>
        </div>
        {notes ? (
          <pre className="whitespace-pre-wrap text-sm text-slate-700 bg-slate-50 rounded-lg p-4 font-sans">{notes}</pre>
        ) : (
          <p className="text-sm text-slate-500">Click "Generate notes" for AI-written study material at your level.</p>
        )}
      </div>

      <div className="card">
        <h2 className="font-semibold text-slate-800 mb-3">Learning materials</h2>
        <ul className="space-y-2 mb-4">
          {materials.map((m) => (
            <li key={m.id}>
              <a href={m.url} target="_blank" rel="noreferrer" className="text-brand-600 hover:underline text-sm">
                {m.title} ({m.format || m.resource_type})
              </a>
            </li>
          ))}
          {materials.length === 0 && <p className="text-sm text-slate-500">No materials uploaded yet.</p>}
        </ul>

        <form onSubmit={handleUpload} className="flex flex-wrap gap-2 items-center border-t border-slate-100 pt-4">
          <input
            type="text" placeholder="Material title" value={uploadTitle}
            onChange={(e) => setUploadTitle(e.target.value)}
            className="border border-slate-300 rounded-lg px-3 py-1.5 text-sm flex-1 min-w-[160px]"
          />
          <input
            type="file" onChange={(e) => setUploadFile(e.target.files[0])}
            className="text-sm"
          />
          <button type="submit" disabled={uploading} className="btn-secondary text-sm">
            {uploading ? "Uploading…" : "Upload to Cloudinary"}
          </button>
        </form>
      </div>
    </div>
  );
}
