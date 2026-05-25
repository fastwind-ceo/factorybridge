import Link from 'next/link';
import { PublicHeader } from '@/components/PublicHeader';

export default function OperatorEntryPage() {
  return (
    <main className="page public-page">
      <PublicHeader />
      <section className="card public-section">
        <div className="kicker">Platform operations</div>
        <h1>Operator Panel</h1>
        <p>
          The operator workspace controls RFQ moderation, supplier verification, tender flow, quote review and landed-cost preparation.
        </p>

        <div className="grid grid-3" style={{ marginTop: 24 }}>
          <Link className="card role-card" href="/admin">
            <span className="badge">Control center</span>
            <h2>Open admin panel</h2>
            <p>Go to the current operator dashboard and RFQ moderation queue.</p>
            <strong>Open panel →</strong>
          </Link>

          <div className="card role-card">
            <span className="badge amber">Review</span>
            <h2>RFQ quality gate</h2>
            <p>Check completeness, category, supplier targeting and commercial readiness.</p>
            <strong>Connected to admin queue</strong>
          </div>

          <div className="card role-card">
            <span className="badge green">Execution</span>
            <h2>Tender supervision</h2>
            <p>Coordinate supplier invitations, quote comparison and customer-ready offer packages.</p>
            <strong>Planned expansion</strong>
          </div>
        </div>
      </section>
    </main>
  );
}
