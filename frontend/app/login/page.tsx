import Link from 'next/link';
export default function LoginPage() {
  return <main className="page" style={{ display: 'grid', placeItems: 'center', padding: 24 }}><div className="card" style={{ width: '100%', maxWidth: 460 }}><div className="kicker">Customer portal</div><h1>Sign in</h1><form className="form"><div className="field"><span className="label">Email</span><input className="input" defaultValue="customer@example.com" /></div><div className="field"><span className="label">Password</span><input className="input" type="password" defaultValue="password" /></div><Link className="btn" href="/dashboard">Open dashboard</Link></form><p>No account? <Link href="/register" style={{ color: '#1d4ed8', fontWeight: 700 }}>Register</Link></p></div></main>;
}
