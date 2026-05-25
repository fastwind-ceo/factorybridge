import { AdminShell } from '@/components/AdminShell';
import { StatusBadge } from '@/components/StatusBadge';
import { adminQuotes } from '@/lib/adminMockData';

export default function AdminQuotesPage() {
  return (
    <AdminShell>
      <div className="topbar"><div><div className="kicker">Quote review</div><h1>Quote review</h1><p>Compare supplier pricing, MOQ, lead time, risk and commercial conditions.</p></div></div>
      <section className="card">
        <table className="table">
          <thead><tr><th>Quote</th><th>RFQ</th><th>Supplier</th><th>Unit</th><th>MOQ</th><th>Lead</th><th>Risk</th><th>Status</th></tr></thead>
          <tbody>{adminQuotes.map((q) => <tr key={q.quote}><td>{q.quote}</td><td>{q.rfq}</td><td>{q.supplier}</td><td>{q.unit}</td><td>{q.moq}</td><td>{q.lead}</td><td><StatusBadge status={q.risk} /></td><td><StatusBadge status={q.status} /></td></tr>)}</tbody>
        </table>
      </section>
    </AdminShell>
  );
}
