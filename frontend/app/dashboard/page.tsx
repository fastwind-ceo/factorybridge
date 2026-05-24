const stats = [
  { title: 'Open RFQ', value: '18' },
  { title: 'Invited Suppliers', value: '126' },
  { title: 'Received Quotes', value: '43' },
]

export default function DashboardPage() {
  return (
    <main className="container">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 28 }}>
        <div>
          <h1>Customer Dashboard</h1>
          <p className="muted">Manage RFQs, quotes and landed cost calculations.</p>
        </div>

        <button className="button">Create RFQ</button>
      </div>

      <section className="grid grid-3">
        {stats.map((item) => (
          <div className="card" key={item.title}>
            <div className="muted">{item.title}</div>
            <div style={{ fontSize: 34, fontWeight: 800, marginTop: 10 }}>{item.value}</div>
          </div>
        ))}
      </section>

      <section className="card" style={{ marginTop: 24 }}>
        <h2>Recent RFQs</h2>

        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr>
              <th align="left">RFQ</th>
              <th align="left">Process</th>
              <th align="left">Status</th>
              <th align="left">Quotes</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Aluminum housing casting</td>
              <td>Die Casting</td>
              <td>Supplier bidding</td>
              <td>7</td>
            </tr>
            <tr>
              <td>Injection molded enclosure</td>
              <td>Plastic Injection</td>
              <td>Operator review</td>
              <td>3</td>
            </tr>
          </tbody>
        </table>
      </section>
    </main>
  )
}
