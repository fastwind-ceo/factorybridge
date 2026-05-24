const stages = [
  {
    title: 'Customer RFQ',
    description: 'Customer uploads drawings, models and commercial requirements.',
  },
  {
    title: 'AI Review',
    description: 'Platform validates completeness, process type and manufacturability signals.',
  },
  {
    title: 'Operator Moderation',
    description: 'Operators review supplier targeting and procurement strategy.',
  },
  {
    title: 'Supplier Tender',
    description: 'Chinese manufacturers submit quotations and lead times.',
  },
  {
    title: 'Landed Cost',
    description: 'Platform calculates logistics, customs and delivered cost scenarios.',
  },
  {
    title: 'Order Execution',
    description: 'Customer selects supplier and launches execution workflow.',
  },
]

export default function WorkflowPage() {
  return (
    <main className="container">
      <div style={{ marginBottom: 28 }}>
        <h1>FactoryBridge Workflow</h1>
        <p className="muted">End-to-end industrial sourcing and tender workflow.</p>
      </div>

      <div className="grid">
        {stages.map((stage, index) => (
          <div key={stage.title} className="card">
            <div className="muted">STEP {index + 1}</div>
            <h2>{stage.title}</h2>
            <p>{stage.description}</p>
          </div>
        ))}
      </div>
    </main>
  )
}
