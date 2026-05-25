import Link from 'next/link';
import { MetricCard } from '@/components/MetricCard';
import { PublicHeader } from '@/components/PublicHeader';

const roleCards = [
  {
    title: 'Customer Portal',
    href: '/customer',
    badge: 'For buyers',
    text: 'Create manufacturing RFQs, upload drawings or models, track supplier quotes and compare landed-cost scenarios.',
  },
  {
    title: 'Supplier Portal',
    href: '/supplier',
    badge: 'For factories',
    text: 'Receive structured RFQs, confirm capabilities, submit quotes and manage production opportunities.',
  },
  {
    title: 'Operator Panel',
    href: '/operator',
    badge: 'For platform team',
    text: 'Moderate requests, verify suppliers, control tender flow and prepare customer-ready offer packages.',
  },
];

const workflow = ['RFQ intake', 'AI review', 'Supplier tender', 'Landed cost', 'Order execution'];
const categories = ['CNC machining', 'Metal casting', 'Plastic molding', 'Stamping', 'Rubber molding', 'Sheet metal', 'Tooling', 'Assembly'];

export default function HomePage() {
  return (
    <main className="page public-page">
      <PublicHeader />

      <section className="hero">
        <div className="kicker" style={{ color: '#a5f3fc' }}>FactoryBridge by Fast Wind</div>
        <h1>AI-assisted tender platform for custom manufacturing in China.</h1>
        <p>
          Customers submit structured RFQs with drawings, models and delivery requirements. Chinese suppliers respond with comparable quotes, while operators control quality, readiness and landed-cost logic.
        </p>
        <div className="hero-actions">
          <Link className="btn secondary" href="/rfqs/new">Create RFQ</Link>
          <Link className="btn" href="/workflow" style={{ background: '#0f172a' }}>View workflow</Link>
        </div>
      </section>

      <section className="grid grid-3 public-section">
        <MetricCard label="Workflow" value="RFQ → Quote → Cost" hint="Managed tender flow for industrial manufacturing requests." />
        <MetricCard label="AI Layer" value="Completeness" hint="Missing fields, process suggestion and supplier-ready brief." />
        <MetricCard label="Commercial" value="Landed Cost" hint="Factory price, logistics, taxes, margin and final customer price." />
      </section>

      <section className="grid grid-3 public-section">
        {roleCards.map((card) => (
          <Link className="card role-card" key={card.href} href={card.href}>
            <span className="badge">{card.badge}</span>
            <h2>{card.title}</h2>
            <p>{card.text}</p>
            <strong>Open workspace →</strong>
          </Link>
        ))}
      </section>

      <section className="card public-section">
        <div className="kicker">Platform workflow</div>
        <h2>From customer request to executable order</h2>
        <div className="workflow-strip">
          {workflow.map((item, index) => (
            <div className="workflow-step" key={item}>
              <span>{index + 1}</span>
              <strong>{item}</strong>
            </div>
          ))}
        </div>
      </section>

      <section className="grid grid-4 public-section">
        {categories.map((x) => <div className="card" key={x}><strong>{x}</strong><p>Supplier matching and RFQ workflow ready for category expansion.</p></div>)}
      </section>
    </main>
  );
}
