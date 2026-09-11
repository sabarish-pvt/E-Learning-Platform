const STYLES = {
  beginner: "bg-emerald-100 text-emerald-700",
  intermediate: "bg-amber-100 text-amber-700",
  advanced: "bg-rose-100 text-rose-700",
};

export default function DifficultyBadge({ level }) {
  if (!level) return null;
  const classes = STYLES[level] || "bg-slate-100 text-slate-700";
  return <span className={`badge ${classes}`}>{level}</span>;
}
