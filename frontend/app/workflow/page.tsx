import Link from 'next/link';
import { StatusBadge } from '@/components/StatusBadge';

const workflow = [
  ['Customer', 'Create RFQ', 'Customer uploads structured request, files and delivery requirements.'],
  ['AI', 'Review RFQ', 'Completeness score, missing fields, process suggestion and supplier brief are generated.'],
  ['Operator', 'Approve & invite', 'Operator approves RFQ and invites selected Chinese suppliers.'],
  ['Supplier', 'Submit quote', 'Supplier accepts invitation and sends price, MOQ, lead time and terms.'],
  ['Operator', 'Landed cost', 'Operator calculates delivered price with logistics, duties, VAT, platform fee and margin.'],
  ['Customer', 'Accept quote', 'Customer reviews safe comparison and accepts preferred quote.'],
  ['Operator', 'Create order', 'Accepted quote becomes managed production order with timeline.'],
];

export default function WorkflowPage() {
  return (
    <main className="container">
      <div className="topbar">
        <div>
          <div className="kicker">STEP 016</div>
          <h1>Full Workflow Integration</h1>
          <p>One connected FactoryBridge operating flow across customer, operator and supplier roles.</p>
        </div>
        <Link className="btn" href="/admin">Open operator panel</Link>
      </div>
      <section className="card">
        <h2>Integrated RFQ → Order flow</h2>
        <div className="timeline">
          {workflow.map(([role, title, note], index) => (
            <div className="timeline-item" key={title}>
              <div className="timeline-dot">{index + 1}</div>
              <div>
                <div><StatusBadge status={role} /> <strong>{title}</strong></div>
                <p>{note}</p>
              </div>
            </div>
          ))}
        </div>
      </section>
      <section className="grid grid-3" style={{ marginTop: 20 }}>
        <div className="card"><h3>Customer proof</h3><p>RFQ creation, AI result, quote comparison and landed-cost view are connected.</p></div>
        <div className="card"><h3>Supplier proof</h3><p>Supplier can only access invited RFQs and submit quote through controlled tender flow.</p></div>
        <div className="card"><h3>Operator proof</h3><p>Operator controls approval, invitations, quotes, calculations, orders and audit visibility.</p></div>
      </section>
    </main>
  );
}
