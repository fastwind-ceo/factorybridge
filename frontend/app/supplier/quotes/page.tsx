import { SupplierShell } from '@/components/SupplierShell';
import { supplierQuotes } from '@/lib/supplierMockData';
import { StatusBadge } from '@/components/StatusBadge';

export default function SupplierQuotesPage() {
  return <SupplierShell><div className="kicker">My quotes</div><h1>Submitted supplier quotations</h1><div className="card"><table className="table"><thead><tr><th>RFQ</th><th>Unit price</th><th>MOQ</th><th>Sample</th><th>Lead time</th><th>Status</th></tr></thead><tbody>{supplierQuotes.map((q) => <tr key={q.rfq}><td><strong>{q.rfq}</strong><br/><span style={{ color: '#64748b' }}>{q.title}</span></td><td>{q.unit}</td><td>{q.moq}</td><td>{q.sample}</td><td>{q.lead}</td><td><StatusBadge status={q.status}/></td></tr>)}</tbody></table></div></SupplierShell>;
}
