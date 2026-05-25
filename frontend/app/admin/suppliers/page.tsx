import { AdminShell } from '@/components/AdminShell';
import { adminSuppliers } from '@/lib/adminMockData';

export default function AdminSuppliersPage() {
  return (
    <AdminShell>
      <div className="topbar"><div><div className="kicker">Supplier verification</div><h1>Supplier verification</h1><p>Review manufacturing capabilities, verification level, response time and production fit.</p></div></div>
      <div className="card">
        <table className="table">
          <thead><tr><th>Supplier</th><th>Process</th><th>City</th><th>Verification</th><th>Rating</th><th>Response</th><th>Actions</th></tr></thead>
          <tbody>{adminSuppliers.map((s) => <tr key={s.id}><td><strong>{s.name}</strong></td><td>{s.process}</td><td>{s.city}</td><td>{s.verification}</td><td>{s.rating}</td><td>{s.response}</td><td><button className="btn ghost">Verify</button></td></tr>)}</tbody>
        </table>
      </div>
    </AdminShell>
  );
}
