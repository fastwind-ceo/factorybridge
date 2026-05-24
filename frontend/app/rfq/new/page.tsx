export default function NewRfqPage() {
  return (
    <main className="container">
      <div className="card" style={{ maxWidth: 860, margin: '24px auto' }}>
        <h1>Create RFQ</h1>
        <p className="muted">Structure a manufacturing request with technical, commercial and logistics information.</p>

        <div className="grid" style={{ marginTop: 24 }}>
          <input className="input" placeholder="Project title" />
          <select className="input" defaultValue="CNC_MACHINING">
            <option value="CNC_MACHINING">CNC machining</option>
            <option value="DIE_CASTING">Metal casting</option>
            <option value="INJECTION_MOLDING">Plastic injection molding</option>
            <option value="STAMPING">Stamping</option>
            <option value="FABRICATION">Fabrication</option>
          </select>
          <textarea className="input" placeholder="Technical description, material, tolerances, standards" rows={6} />
          <textarea className="input" placeholder="Quantity, batches, annual demand, target delivery address" rows={4} />
          <div style={{ border: '1px dashed var(--border)', borderRadius: 14, padding: 18 }}>
            <strong>Attachments</strong>
            <p className="muted">Upload drawings, 3D models, specifications and quality requirements.</p>
          </div>
          <button className="button">Submit for AI review</button>
        </div>
      </div>
    </main>
  )
}
