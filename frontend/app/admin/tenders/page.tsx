import { AdminShell } from '@/components/AdminShell';
import { StatusBadge } from '@/components/StatusBadge';
import { tenderInvitations } from '@/lib/adminMockData';

export default function AdminTendersPage() {
  return (
    <AdminShell>
      <div className="topbar"><div><div className="kicker">Tender control</div><h1>Tender control panel</h1><p>Track supplier invitations, access levels, deadlines and quote progress.</p></div></div>
      <section className="card">
        <table className="table">
          <thead><tr><th>RFQ</th><th>Supplier</th><th>Access</th><th>Status</th><th>Deadline</th><th>Action</th></tr></thead>
          <tbody>{tenderInvitations.map((i) => <tr key={`${i.rfq}-${i.supplier}`}><td>{i.rfq}</td><td>{i.supplier}</td><td>{i.access}</td><td><StatusBadge status={i.status} /></td><td>{i.deadline}</td><td><button className="btn ghost">Adjust access</button></td></tr>)}</tbody>
        </table>
      </section>
    </AdminShell>
  );
}
