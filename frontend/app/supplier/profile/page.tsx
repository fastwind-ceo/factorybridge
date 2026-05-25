import { SupplierShell } from '@/components/SupplierShell';
import { supplierCapabilities, supplierProfile } from '@/lib/supplierMockData';

export default function SupplierProfilePage() {
  return (
    <SupplierShell>
      <div className="kicker">Supplier profile</div>
      <h1>Manufacturing capability profile</h1>
      <div className="split">
        <section className="card">
          <h2>Company information</h2>
          <div className="grid grid-2">
            <div className="field"><span className="label">English name</span><input className="input" defaultValue={supplierProfile.company}/></div>
            <div className="field"><span className="label">Chinese name</span><input className="input" defaultValue={supplierProfile.chineseName}/></div>
            <div className="field"><span className="label">Province</span><input className="input" defaultValue={supplierProfile.province}/></div>
            <div className="field"><span className="label">City</span><input className="input" defaultValue={supplierProfile.city}/></div>
            <div className="field"><span className="label">Export markets</span><input className="input" defaultValue={supplierProfile.exportMarkets}/></div>
            <div className="field"><span className="label">Verification</span><input className="input" defaultValue={supplierProfile.verification}/></div>
          </div>
          <div style={{ marginTop: 18 }}><button className="btn" type="button">Save supplier profile</button></div>
        </section>
        <aside className="card">
          <h2>Operator matching notes</h2>
          <p>This supplier is suitable for CNC aluminum and stainless steel RFQs with low-to-medium MOQ and export-ready documentation.</p>
          <span className="badge green">Export to Russia ready</span>
        </aside>
      </div>
      <section className="card" style={{ marginTop: 22 }}>
        <h2>Capabilities</h2>
        <table className="table"><thead><tr><th>Process</th><th>Materials</th><th>MOQ</th><th>Lead time</th><th>Tags</th></tr></thead><tbody>{supplierCapabilities.map((c) => <tr key={c.process}><td><strong>{c.process}</strong></td><td>{c.materials}</td><td>{c.moq}</td><td>{c.lead}</td><td>{c.tags.join(', ')}</td></tr>)}</tbody></table>
      </section>
    </SupplierShell>
  );
}
