import Link from 'next/link';
import { StatusBadge } from './StatusBadge';
import { mockRfqs } from '@/lib/mockData';

export function RFQTable() {
  return (
    <table className="table">
      <thead><tr><th>RFQ</th><th>Category</th><th>Qty</th><th>Status</th><th>Quotes</th><th></th></tr></thead>
      <tbody>{mockRfqs.map((rfq) => (
        <tr key={rfq.id}>
          <td><strong>{rfq.number}</strong><br/><span style={{color:'#64748b'}}>{rfq.title}</span></td>
          <td>{rfq.category}</td><td>{rfq.quantity}</td><td><StatusBadge status={rfq.status}/></td><td>{rfq.quotes}</td>
          <td><Link className="btn ghost" href={`/rfqs/${rfq.id}`}>Open</Link></td>
        </tr>
      ))}</tbody>
    </table>
  );
}
