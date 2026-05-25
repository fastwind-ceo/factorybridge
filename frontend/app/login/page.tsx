import Link from 'next/link';
import { PublicHeader } from '@/components/PublicHeader';

export default function LoginPage() {
  return (
    <main className="page public-page">
      <PublicHeader />

      <section style={{ display: 'grid', placeItems: 'center', padding: '40px 0' }}>
        <div className="card" style={{ width: '100%', maxWidth: 520 }}>
          <div className="kicker">FactoryBridge access</div>
          <h1>Sign in</h1>

          <p>
            Current authentication is running in MVP/demo mode. Backend auth and role permissions will be connected in the next backend stage.
          </p>

          <form className="form" style={{ marginTop: 18 }}>
            <div className="field">
              <span className="label">Portal role</span>
              <select className="select" defaultValue="customer">
                <option value="customer">Customer</option>
                <option value="supplier">Supplier</option>
                <option value="operator">Operator</option>
              </select>
            </div>

            <div className="field">
              <span className="label">Email</span>
              <input className="input" defaultValue="user@factorybridge.ai" />
            </div>

            <div className="field">
              <span className="label">Password</span>
              <input className="input" type="password" defaultValue="password" />
            </div>

            <div className="grid grid-3">
              <Link className="btn" href="/dashboard">Customer</Link>
              <Link className="btn secondary" href="/supplier">Supplier</Link>
              <Link className="btn ghost" href="/admin">Operator</Link>
            </div>
          </form>

          <p style={{ marginTop: 18 }}>
            No account? <Link href="/register" style={{ color: '#1d4ed8', fontWeight: 700 }}>Register</Link>
          </p>
        </div>
      </section>
    </main>
  );
}
