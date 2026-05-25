export function MetricCard({ label, value, hint }: { label: string; value: string | number; hint?: string }) {
  return <div className="card"><div className="kicker">{label}</div><div className="metric">{value}</div>{hint ? <p>{hint}</p> : null}</div>;
}
