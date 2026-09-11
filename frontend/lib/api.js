/**
 * Thin axios wrapper around the FastAPI backend. Centralizing calls here
 * means components never hardcode a URL or repeat error handling.
 */
import axios from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const client = axios.create({ baseURL: API_URL });

export const api = {
  // Students
  register: (data) => client.post("/students/register", data).then((r) => r.data),
  login: (data) => client.post("/students/login", data).then((r) => r.data),
  getStudent: (id) => client.get(`/students/${id}`).then((r) => r.data),

  // Courses / topics
  listCourses: () => client.get("/courses").then((r) => r.data),
  getCourse: (id) => client.get(`/courses/${id}`).then((r) => r.data),
  createCourse: (data) => client.post("/courses", data).then((r) => r.data),
  addTopic: (courseId, data) => client.post(`/courses/${courseId}/topics`, data).then((r) => r.data),
  getTopic: (id) => client.get(`/topics/${id}`).then((r) => r.data),
  getTopicMaterials: (id) => client.get(`/topics/${id}/materials`).then((r) => r.data),
  getPracticeNotes: (id, difficulty) =>
    client.get(`/topics/${id}/practice-notes`, { params: { difficulty } }).then((r) => r.data),

  // Materials (Cloudinary upload)
  uploadMaterial: (formData) =>
    client.post("/materials/upload", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    }).then((r) => r.data),

  // Quizzes
  generateQuizForStudent: (studentId, topicId, numQuestions = 5) =>
    client
      .post("/quizzes/generate-for-student", null, {
        params: { student_id: studentId, topic_id: topicId, num_questions: numQuestions },
      })
      .then((r) => r.data),
  getQuiz: (id) => client.get(`/quizzes/${id}`).then((r) => r.data),
  submitQuiz: (data) => client.post("/quizzes/submit", data).then((r) => r.data),

  // Progress
  getProgress: (studentId) => client.get(`/progress/${studentId}`).then((r) => r.data),
  getProgressSummary: (studentId) => client.get(`/progress/${studentId}/summary`).then((r) => r.data),

  // ML analysis
  recommendDifficulty: (studentId) =>
    client.get(`/analysis/${studentId}/recommend-difficulty`).then((r) => r.data),
  analysisHistory: (studentId) => client.get(`/analysis/${studentId}/history`).then((r) => r.data),
};

export default api;
