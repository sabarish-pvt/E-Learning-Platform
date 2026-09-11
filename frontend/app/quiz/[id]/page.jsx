"use client";

import { useEffect, useState, useRef } from "react";
import { useParams, useRouter } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import DifficultyBadge from "@/components/DifficultyBadge";
import api from "@/lib/api";

export default function QuizPage() {
  const { id } = useParams();
  const router = useRouter();
  const { student, updateStudent } = useAuth();

  const [quiz, setQuiz] = useState(null);
  const [answers, setAnswers] = useState({});     // questionId -> "A"|"B"|"C"|"D"
  const [result, setResult] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const questionStartTimes = useRef({});

  useEffect(() => {
    if (!student) {
      router.push("/");
      return;
    }
    api.getQuiz(id).then((data) => {
      setQuiz(data);
      const now = Date.now();
      data.questions.forEach((q) => (questionStartTimes.current[q.id] = now));
    });
  }, [id, student]);

  const selectOption = (questionId, option) => {
    setAnswers((prev) => ({ ...prev, [questionId]: option }));
  };

  const handleSubmit = async () => {
    setSubmitting(true);
    try {
      const payload = {
        student_id: student.id,
        quiz_id: quiz.id,
        answers: quiz.questions.map((q) => ({
          question_id: q.id,
          selected_option: answers[q.id] || "",
          time_taken_seconds: (Date.now() - (questionStartTimes.current[q.id] || Date.now())) / 1000,
        })),
      };
      const res = await api.submitQuiz(payload);
      setResult(res);
      const refreshedStudent = await api.getStudent(student.id);
      updateStudent(refreshedStudent);
    } finally {
      setSubmitting(false);
    }
  };

  if (!quiz) return <p className="text-slate-500">Loading quiz…</p>;

  if (result) {
    const gradedById = Object.fromEntries(result.graded_answers.map((g) => [g.question_id, g]));
    return (
      <div className="space-y-6">
        <div className="card text-center">
          <h1 className="text-2xl font-bold text-slate-900">Score: {result.score_percent}%</h1>
          <p className="text-slate-500 mt-1">
            {result.correct_count} / {result.total_questions} correct
          </p>
          <div className="mt-3 flex items-center justify-center gap-2 text-sm text-slate-500">
            Your next recommended difficulty: <DifficultyBadge level={result.updated_difficulty} />
          </div>
        </div>

        <div className="space-y-4">
          {quiz.questions.map((q) => {
            const graded = gradedById[q.id];
            return (
              <div key={q.id} className={`card border-l-4 ${graded?.is_correct ? "border-l-emerald-400" : "border-l-rose-400"}`}>
                <p className="font-medium text-slate-800">{q.prompt}</p>
                <p className="text-sm mt-2">
                  Your answer: <strong>{graded?.selected_option || "—"}</strong>
                  {!graded?.is_correct && (
                    <> · Correct answer: <strong>{graded?.correct_option}</strong></>
                  )}
                </p>
                {graded?.explanation && (
                  <p className="text-sm text-slate-600 mt-2 bg-slate-50 rounded-lg p-3">{graded.explanation}</p>
                )}
              </div>
            );
          })}
        </div>

        <button onClick={() => router.push("/dashboard")} className="btn-primary w-full">
          Back to dashboard
        </button>
      </div>
    );
  }

  const allAnswered = quiz.questions.every((q) => answers[q.id]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-slate-900">{quiz.title}</h1>
        <DifficultyBadge level={quiz.difficulty} />
      </div>

      <div className="space-y-4">
        {quiz.questions.map((q, idx) => (
          <div key={q.id} className="card">
            <p className="font-medium text-slate-800 mb-3">{idx + 1}. {q.prompt}</p>
            <div className="space-y-2">
              {["A", "B", "C", "D"].map((letter) => {
                const text = q[`option_${letter.toLowerCase()}`];
                const selected = answers[q.id] === letter;
                return (
                  <button
                    key={letter}
                    onClick={() => selectOption(q.id, letter)}
                    className={`w-full text-left px-4 py-2.5 rounded-lg border text-sm transition-colors ${
                      selected ? "border-brand-500 bg-brand-50 text-brand-700" : "border-slate-200 hover:bg-slate-50"
                    }`}
                  >
                    <span className="font-semibold mr-2">{letter}.</span>{text}
                  </button>
                );
              })}
            </div>
          </div>
        ))}
      </div>

      <button onClick={handleSubmit} disabled={!allAnswered || submitting} className="btn-primary w-full">
        {submitting ? "Grading…" : "Submit quiz"}
      </button>
    </div>
  );
}
