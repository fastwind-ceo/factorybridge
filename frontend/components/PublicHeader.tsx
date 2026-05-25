import Link from 'next/link';

const publicNav = [
  ['Home', '/'],
  ['Customer Portal', '/customer'],
  ['Supplier Portal', '/supplier'],
  ['Operator Panel', '/operator'],
];

export function PublicHeader() {
  return (
    <header className="public-header">
      <Link href="/" className="public-brand">FactoryBridge <span>by Fast Wind</span></Link>
      <nav className="public-nav">
        {publicNav.map(([label, href]) => <Link key={href} href={href}>{label}</Link>)}
      </nav>
      <div className="public-actions">
        <Link className="btn ghost" href="/login">Sign in</Link>
        <Link className="btn" href="/register">Start RFQ</Link>
      </div>
    </header>
  );
}
