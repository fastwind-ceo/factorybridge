import { AdminShell } from '@/components/AdminShell';
import { StatusBadge } from '@/components/StatusBadge';
import { adminQuotes, adminRfqs, adminSuppliers } from '@/lib/adminMockData';

export default async function AdminRfqDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const rfq = adminRfqs.find((item) => item.id === id) || adminRfqs[0];
  return (
    <AdminShell>
      <div className="topbar">
        <div>
          <div className="kicker">RFQ moderation detail</div>
          <h1>{rfq.number}</h1>
          <p>{rfq.title}</p>
        </div>
        <StatusBadge status={rfq.status} />
      </div>
      <div className="grid grid-2">
        <section className="card">
          <h2>Operator review</h2>
          <p><strong>Customer:</strong> {rfq.customer}</p>
          <p><strong>Category:</strong> {rfq.category}</p>
          <p><strong>AI completeness score:</strong> {rfq.aiScore}%</p>
          <div className="grid grid-2">
            <button className="btn">Approve for tender</button>
            <button className="btn secondary">Request clarification</button>
            <button className="btn ghost">Assign engineer</button>
            <button className="btn ghost">Reject RFQ</button>
          </div>
        </section>
        <section className="card">
          <h2>AI risk flags</h2>
          <p><span className="badge amber">MISSING_SURFACE_FINISH</span></p>
          <p><span className="badge green">PROCESS_CLASSIFIED</span></p>
          <p><span className="badge amber">LOGISTICS_DATA_PARTIAL</span></p>
        </section>
      </div>
      <section className="card" style={{ marginTop: 20 }}>
        <h2>Supplier matching panel</h2>
        <table className="table">
          <thead><tr><th>Supplier</th><th>Process</th><th>City</th><th>Verification</th><th>Action</th></tr></thead>
          <tbody>{adminSuppliers.map((s) => <tr key={s.id}><td>{s.name}</td><td>{s.process}</td><td>{s.city}</td><td>{s.verification}</td><td><button className="btn ghost">Invite</button></td></tr>)}</tbody>
        </table>
      </section>
      <section className="card" style={{ marginTop: 20 }}>
        <h2>Quote review</h2>
        <table className="table">
          <thead><tr><th>Quote</th><th>Supplier</th><th>Unit</th><th>MOQ</th><th>Lead</th><th>Risk</th></tr></thead>
          <tbody>{adminQuotes.slice(0, 2).map((q) => <tr key={q.quote}><td>{q.quote}</td><td>{q.supplier}</td><td>{q.unit}</td><td>{q.moq}</td><td>{q.lead}</td><td><StatusBadge status={q.risk} /></td></tr>)}</tbody>
        </table>
      </section>
    </AdminShell>
  );
}
