import { AdminShell } from '@/components/AdminShell';
import { auditRows } from '@/lib/adminMockData';

export default function AdminAuditPage() {
  return (
    <AdminShell>
      <div className="topbar"><div><div className="kicker">Audit logs</div><h1>Audit logs</h1><p>Trace critical actions across RFQ, quote, landed cost, files and order workflow.</p></div></div>
      <section className="card">
        <table className="table">
          <thead><tr><th>Actor</th><th>Action</th><th>Object</th><th>Time</th></tr></thead>
          <tbody>{auditRows.map((row) => <tr key={`${row.action}-${row.time}`}><td>{row.actor}</td><td>{row.action}</td><td>{row.object}</td><td>{row.time}</td></tr>)}</tbody>
        </table>
      </section>
    </AdminShell>
  );
}
