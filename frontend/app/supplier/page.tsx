import Link from 'next/link';
import { SupplierShell } from '@/components/SupplierShell';
import { MetricCard } from '@/components/MetricCard';
import { invitedRfqs, supplierProfile, supplierQuotes } from '@/lib/supplierMockData';
import { StatusBadge } from '@/components/StatusBadge';

export default function SupplierDashboardPage() {
  return (
    <SupplierShell>
      <div className="topbar">
        <div>
          <div className="kicker">Supplier dashboard</div>
          <h1>{supplierProfile.company}</h1>
          <p>Manage invited RFQs, submit structured quotations and keep your manufacturing capabilities ready for operator matching.</p>
        </div>
        <Link className="btn" href="/supplier/rfqs">View RFQs</Link>
      </div>
      <section className="grid grid-4">
        <MetricCard label="Available RFQs" value={invitedRfqs.length} />
        <MetricCard label="Submitted quotes" value={supplierQuotes.filter((q) => q.status === 'SUBMITTED').length} />
        <MetricCard label="Verification" value="Doc" hint={supplierProfile.verification} />
        <MetricCard label="Response" value={supplierProfile.responseTime} />
      </section>
      <section className="card" style={{ marginTop: 22 }}>
        <h2>Recent invitations</h2>
        <table className="table">
          <thead><tr><th>RFQ</th><th>Process</th><th>Qty</th><th>Access</th><th>Status</th><th></th></tr></thead>
          <tbody>{invitedRfqs.map((rfq) => <tr key={rfq.id}><td><strong>{rfq.number}</strong><br/><span style={{ color: '#64748b' }}>{rfq.title}</span></td><td>{rfq.process}</td><td>{rfq.qty}</td><td>{rfq.access}</td><td><StatusBadge status={rfq.status}/></td><td><Link className="btn ghost" href={`/supplier/rfqs/${rfq.id}`}>Open</Link></td></tr>)}</tbody>
        </table>
      </section>
    </SupplierShell>
  );
}
