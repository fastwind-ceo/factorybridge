import Link from 'next/link';
import { SupplierShell } from '@/components/SupplierShell';
import { invitedRfqs } from '@/lib/supplierMockData';
import { StatusBadge } from '@/components/StatusBadge';

export default function SupplierRFQsPage() {
  return <SupplierShell><div className="topbar"><div><div className="kicker">Available RFQs</div><h1>Invited manufacturing tenders</h1><p>Only RFQs explicitly invited by FactoryBridge operator are visible here.</p></div></div><div className="card"><table className="table"><thead><tr><th>RFQ</th><th>Process</th><th>Quantity</th><th>Deadline</th><th>Access</th><th>Status</th><th></th></tr></thead><tbody>{invitedRfqs.map((rfq) => <tr key={rfq.id}><td><strong>{rfq.number}</strong><br/><span style={{color:'#64748b'}}>{rfq.title}</span></td><td>{rfq.process}</td><td>{rfq.qty}</td><td>{rfq.deadline}</td><td>{rfq.access}</td><td><StatusBadge status={rfq.status}/></td><td><Link className="btn ghost" href={`/supplier/rfqs/${rfq.id}`}>Review</Link></td></tr>)}</tbody></table></div></SupplierShell>;
}
