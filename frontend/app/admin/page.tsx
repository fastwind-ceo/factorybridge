const auditItems = [
  { event: 'Supplier verification approved', actor: 'operator@factorybridge.ai' },
  { event: 'RFQ sent to suppliers', actor: 'operator@factorybridge.ai' },
  { event: 'AI RFQ review completed', actor: 'ai-engine' },
]

export default function AdminPage() {
  return (
    <main className="container">
      <div style={{ marginBottom: 28 }}>
        <h1>Operator / Admin Panel</h1>
        <p className="muted">Moderate RFQs, suppliers, quotes and operational workflow.</p>
      </div>

      <section className="grid grid-3">
        <div className="card">
          <div className="muted">Pending RFQs</div>
          <div style={{ fontSize: 30, fontWeight: 800, marginTop: 10 }}>14</div>
        </div>
        <div className="card">
          <div className="muted">Supplier verifications</div>
          <div style={{ fontSize: 30, fontWeight: 800, marginTop: 10 }}>6</div>
        </div>
        <div className="card">
          <div className="muted">Open orders</div>
          <div style={{ fontSize: 30, fontWeight: 800, marginTop: 10 }}>11</div>
        </div>
      </section>

      <section className="card" style={{ marginTop: 24 }}>
        <h2>Audit stream</h2>

        <div className="grid">
          {auditItems.map((item) => (
            <div key={item.event} style={{ borderBottom: '1px solid var(--border)', paddingBottom: 12 }}>
              <strong>{item.event}</strong>
              <div className="muted">Actor: {item.actor}</div>
            </div>
          ))}
        </div>
      </section>
    </main>
  )
}
