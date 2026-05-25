import { AdminShell } from '@/components/AdminShell';

const rows = [
  ['Factory total', '$6,250'],
  ['Packaging', '$50'],
  ['China logistics', '$200'],
  ['International freight', '$900'],
  ['Customs + duty', '$562'],
  ['VAT', '$1,312'],
  ['Local delivery', '$180'],
  ['Platform fee', '$468'],
  ['Internal margin', '$1,125'],
  ['Risk reserve', '$281'],
];

export default function AdminLandedCostsPage() {
  return (
    <AdminShell>
      <div className="topbar"><div><div className="kicker">Landed cost builder</div><h1>Landed cost builder</h1><p>Build operator-only and customer-facing price calculations for delivered manufacturing orders.</p></div></div>
      <div className="split">
        <section className="card">
          <h2>Cost components</h2>
          <table className="table"><tbody>{rows.map(([name, amount]) => <tr key={name}><td>{name}</td><td><strong>{amount}</strong></td></tr>)}</tbody></table>
        </section>
        <section className="card">
          <h2>Customer-facing result</h2>
          <p className="metric">$19.34 / unit</p>
          <p>Total delivered estimate: <strong>$9,672.44</strong></p>
          <button className="btn">Save calculation version</button>
          <button className="btn secondary" style={{ marginLeft: 10 }}>Create customer view</button>
        </section>
      </div>
    </AdminShell>
  );
}
