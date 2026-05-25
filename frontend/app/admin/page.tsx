import { AdminShell } from '@/components/AdminShell';
import { MetricCard } from '@/components/MetricCard';
import { StatusBadge } from '@/components/StatusBadge';
import { adminMetrics, adminRfqs } from '@/lib/adminMockData';
import Link from 'next/link';

export default function AdminDashboardPage() {
  return (
    <AdminShell>
      <div className="topbar">
        <div>
          <div className="kicker">Operator control center</div>
          <h1>Admin / Operator Panel</h1>
          <p>Managed sourcing workspace for RFQ moderation, supplier control, quote review, landed cost and audit.</p>
        </div>
        <Link className="btn" href="/admin/rfqs">Open RFQ queue</Link>
      </div>
      <section className="grid grid-4">
        {adminMetrics.map((m) => <MetricCard key={m.label} label={m.label} value={m.value} hint={m.note} />)}
      </section>
      <section className="card" style={{ marginTop: 20 }}>
        <h2>RFQ moderation queue</h2>
        <table className="table">
          <thead><tr><th>RFQ</th><th>Customer</th><th>Category</th><th>AI Score</th><th>Status</th><th>Action</th></tr></thead>
          <tbody>
            {adminRfqs.map((rfq) => (
              <tr key={rfq.id}>
                <td><strong>{rfq.number}</strong><br />{rfq.title}</td>
                <td>{rfq.customer}</td>
                <td>{rfq.category}</td>
                <td>{rfq.aiScore}%</td>
                <td><StatusBadge status={rfq.status} /></td>
                <td><Link className="btn ghost" href={`/admin/rfqs/${rfq.id}`}>Moderate</Link></td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </AdminShell>
  );
}
