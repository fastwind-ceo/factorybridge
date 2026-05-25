import { AdminShell } from '@/components/AdminShell';
import { StatusBadge } from '@/components/StatusBadge';
import { adminRfqs } from '@/lib/adminMockData';
import Link from 'next/link';

export default function AdminRfqsPage() {
  return (
    <AdminShell>
      <div className="topbar">
        <div>
          <div className="kicker">RFQ moderation</div>
          <h1>RFQ moderation queue</h1>
          <p>Review AI scores, technical readiness, customer clarification status and tender approval decisions.</p>
        </div>
      </div>
      <div className="card">
        <table className="table">
          <thead><tr><th>RFQ</th><th>Customer</th><th>Category</th><th>AI</th><th>Operator</th><th>Status</th><th>Action</th></tr></thead>
          <tbody>
            {adminRfqs.map((rfq) => (
              <tr key={rfq.id}>
                <td><strong>{rfq.number}</strong><br />{rfq.title}</td>
                <td>{rfq.customer}</td>
                <td>{rfq.category}</td>
                <td>{rfq.aiScore}%</td>
                <td>{rfq.operator}</td>
                <td><StatusBadge status={rfq.status} /></td>
                <td><Link className="btn ghost" href={`/admin/rfqs/${rfq.id}`}>Open</Link></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </AdminShell>
  );
}
