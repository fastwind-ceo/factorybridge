import Link from 'next/link';
import { MetricCard } from '@/components/MetricCard';

export default function HomePage() {
  return (
    <main className="page" style={{ padding: 24 }}>
      <section className="hero">
        <div className="kicker" style={{ color: '#a5f3fc' }}>FactoryBridge by Fast Wind</div>
        <h1>AI-assisted manufacturing tender platform for China custom production.</h1>
        <p>
          Customers upload drawings, 3D models, samples or tender requirements. FactoryBridge normalizes RFQs, collects structured supplier quotes and prepares landed-cost calculations to the delivery address.
        </p>
        <div className="hero-actions">
          <Link className="btn secondary" href="/register">Create customer account</Link>
          <Link className="btn" href="/login" style={{ background: '#0f172a' }}>Open portal</Link>
        </div>
      </section>
      <section className="grid grid-3" style={{ maxWidth: 1180, margin: '0 auto 36px' }}>
        <MetricCard label="Workflow" value="RFQ → Quote → Cost" hint="Managed tender flow for industrial manufacturing requests." />
        <MetricCard label="AI Layer" value="Completeness" hint="Missing fields, process suggestion and supplier-ready brief." />
        <MetricCard label="Commercial" value="Landed Cost" hint="Factory price, logistics, taxes, margin and final customer price." />
      </section>
      <section className="grid grid-4" style={{ maxWidth: 1180, margin: '0 auto' }}>
        {['CNC machining', 'Metal casting', 'Plastic molding', 'Stamping', 'Rubber molding', 'Sheet metal', 'Tooling', 'Assembly'].map((x) => <div className="card" key={x}><strong>{x}</strong><p>Supplier matching and RFQ workflow ready for category expansion.</p></div>)}
      </section>
    </main>
  );
}
