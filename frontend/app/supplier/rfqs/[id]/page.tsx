import { SupplierShell } from '@/components/SupplierShell';
import { StatusBadge } from '@/components/StatusBadge';

export default function SupplierRFQDetailPage() {
  return (
    <SupplierShell>
      <div className="topbar">
        <div>
          <div className="kicker">FB-RFQ-2026-000001</div>
          <h1>Aluminum CNC bracket by drawing</h1>
          <StatusBadge status="ACCEPTED" />
        </div>
        <div style={{ display: 'flex', gap: 10 }}><button className="btn secondary">Decline</button><button className="btn">Accept invitation</button></div>
      </div>
      <div className="grid grid-3">
        <div className="card"><h2>RFQ preview</h2><p>Process: CNC machining</p><p>Material: Aluminum 6061-T6</p><p>Quantity: 500 pcs</p><p>Destination: Moscow, Russia</p></div>
        <div className="card"><h2>Access</h2><p>Technical files require NDA acceptance and operator approval.</p><span className="badge amber">NDA required</span></div>
        <div className="card"><h2>Quote requirements</h2><p>Provide unit price, MOQ, sample cost, production lead time, Incoterms and packaging details.</p></div>
      </div>
      <section className="card" style={{ marginTop: 22 }}>
        <h2>Submit quotation</h2>
        <div className="grid grid-3">
          <div className="field"><span className="label">Unit price, USD</span><input className="input" defaultValue="12.40" /></div>
          <div className="field"><span className="label">MOQ</span><input className="input" defaultValue="300" /></div>
          <div className="field"><span className="label">Tooling cost</span><input className="input" defaultValue="0" /></div>
          <div className="field"><span className="label">Sample cost</span><input className="input" defaultValue="80" /></div>
          <div className="field"><span className="label">Sample lead time</span><input className="input" defaultValue="7 days" /></div>
          <div className="field"><span className="label">Mass production</span><input className="input" defaultValue="25 days" /></div>
          <div className="field"><span className="label">Incoterms</span><select className="select"><option>EXW</option><option>FOB</option><option>CPT</option></select></div>
          <div className="field"><span className="label">Payment terms</span><input className="input" defaultValue="30% deposit, 70% before shipment" /></div>
          <div className="field"><span className="label">Validity</span><input className="input" defaultValue="30 days" /></div>
        </div>
        <div className="field" style={{ marginTop: 14 }}><span className="label">Supplier comments</span><textarea className="textarea" defaultValue="Price is based on attached drawing. Surface finish to be confirmed." /></div>
        <div style={{ marginTop: 18, display: 'flex', gap: 10 }}><button className="btn secondary">Save draft</button><button className="btn">Submit quote</button></div>
      </section>
    </SupplierShell>
  );
}
