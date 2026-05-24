const opportunities = [
  { title: 'CNC aluminum bracket', process: 'CNC Machining', deadline: 'Open', quotes: 'Need quote' },
  { title: 'Plastic injection cover', process: 'Injection Molding', deadline: 'Open', quotes: 'Need quote' },
  { title: 'Stamped steel plate', process: 'Stamping', deadline: 'Pending', quotes: 'Draft quote' },
]

export default function SupplierPage() {
  return (
    <main className="container">
      <div style={{ marginBottom: 28 }}>
        <h1>Supplier Portal</h1>
        <p className="muted">Manage invited RFQs, manufacturing capabilities and supplier quotes.</p>
      </div>

      <section className="grid grid-3">
        <div className="card">
          <div className="muted">Verified capabilities</div>
          <div style={{ fontSize: 30, fontWeight: 800, marginTop: 10 }}>12</div>
        </div>
        <div className="card">
          <div className="muted">Invited RFQs</div>
          <div style={{ fontSize: 30, fontWeight: 800, marginTop: 10 }}>9</div>
        </div>
        <div className="card">
          <div className="muted">Submitted quotes</div>
          <div style={{ fontSize: 30, fontWeight: 800, marginTop: 10 }}>21</div>
        </div>
      </section>

      <section className="card" style={{ marginTop: 24 }}>
        <h2>RFQ invitations</h2>
        <div className="grid">
          {opportunities.map((item) => (
            <div key={item.title} style={{ border: '1px solid var(--border)', borderRadius: 14, padding: 16 }}>
              <strong>{item.title}</strong>
              <div className="muted">Process: {item.process}</div>
              <div className="muted">Status: {item.deadline}</div>
              <button className="button" style={{ marginTop: 12 }}>Open RFQ</button>
            </div>
          ))}
        </div>
      </section>
    </main>
  )
}
