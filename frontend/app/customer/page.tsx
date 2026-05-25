import Link from 'next/link';
import { PublicHeader } from '@/components/PublicHeader';

export default function CustomerPage() {
  return (
    <main className="page public-page">
      <PublicHeader />
      <section className="card public-section">
        <div className="kicker">Customer workspace</div>
        <h1>Customer Portal</h1>
        <p>Create manufacturing requests, track supplier offers and prepare executable landed-cost scenarios.</p>
        <div className="grid grid-3" style={{ marginTop: 24 }}>
          <Link className="card role-card" href="/rfqs/new">
            <span className="badge">Start</span>
            <h2>Create RFQ</h2>
            <p>Open a structured request for drawings, 3D models, samples or recurring supply.</p>
            <strong>New request →</strong>
          </Link>
          <Link className="card role-card" href="/rfqs">
            <span className="badge green">Track</span>
            <h2>My RFQs</h2>
            <p>Review statuses, operator comments and supplier response readiness.</p>
            <strong>Open list →</strong>
          </Link>
          <div className="card role-card">
            <span className="badge amber">Next</span>
            <h2>Cost scenarios</h2>
            <p>Compare factory price, inspection, logistics, customs and final delivery cost.</p>
            <strong>Planned module</strong>
          </div>
        </div>
      </section>
    </main>
  );
}
