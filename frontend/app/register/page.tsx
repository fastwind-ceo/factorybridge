import Link from 'next/link';
import { PublicHeader } from '@/components/PublicHeader';

export default function RegisterPage() {
  return (
    <main className="page public-page">
      <PublicHeader />

      <section style={{ display: 'grid', placeItems: 'center', padding: '40px 0' }}>
        <div className="card" style={{ width: '100%', maxWidth: 760 }}>
          <div className="kicker">FactoryBridge onboarding</div>
          <h1>Create account</h1>
          <p>
            Choose the role that matches your company. This page prepares the onboarding structure for the upcoming backend authentication and verification module.
          </p>

          <div className="grid grid-2" style={{ marginTop: 18 }}>
            <div className="field">
              <span className="label">Company role</span>
              <select className="select" defaultValue="customer">
                <option value="customer">Customer / Buyer</option>
                <option value="supplier">Supplier / Factory</option>
                <option value="operator">Operator / Platform team</option>
              </select>
            </div>

            <div className="field">
              <span className="label">Company name</span>
              <input className="input" placeholder="Example Manufacturing LLC" />
            </div>

            <div className="field">
              <span className="label">Work email</span>
              <input className="input" placeholder="name@company.com" />
            </div>

            <div className="field">
              <span className="label">Password</span>
              <input className="input" type="password" placeholder="Create secure password" />
            </div>
          </div>

          <div className="grid grid-3" style={{ marginTop: 22 }}>
            <Link className="card role-card" href="/customer">
              <span className="badge">Customer</span>
              <h2>Request production</h2>
              <p>Create RFQs and compare supplier quotes.</p>
            </Link>

            <Link className="card role-card" href="/supplier">
              <span className="badge green">Supplier</span>
              <h2>Join tenders</h2>
              <p>Receive RFQs and submit structured quotations.</p>
            </Link>

            <Link className="card role-card" href="/operator">
              <span className="badge amber">Operator</span>
              <h2>Manage platform</h2>
              <p>Moderate RFQs, suppliers and commercial readiness.</p>
            </Link>
          </div>
        </div>
      </section>
    </main>
  );
}
