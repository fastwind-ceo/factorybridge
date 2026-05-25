type Tone = 'blue' | 'green' | 'amber' | 'red';
const statusTone: Record<string, Tone> = {
  DRAFT: 'blue', SUBMITTED: 'amber', AI_REVIEWED: 'green', QUOTING: 'blue', QUOTES_RECEIVED: 'green', CLOSED: 'green', REJECTED: 'red'
};
export function StatusBadge({ status }: { status: string }) {
  const tone = statusTone[status] || 'blue';
  return <span className={`badge ${tone === 'blue' ? '' : tone}`}>{status.replaceAll('_', ' ')}</span>;
}
