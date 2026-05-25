import Link from 'next/link';
import type { ReactNode } from 'react';

const nav = [
  ['Dashboard', '/dashboard'],
  ['Create RFQ', '/rfqs/new'],
  ['My RFQs', '/rfqs'],
  ['Quotes', '/quotes'],
  ['Landed Costs', '/landed-costs'],
  ['Notifications', '/notifications'],
];

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <div className="shell">
      <aside className="sidebar">
        <Link href="/" className="logo">FactoryBridge <span>AI</span></Link>
        <nav className="nav">
          {nav.map(([label, href]) => <Link key={href} href={href}>{label}</Link>)}
        </nav>
      </aside>
      <main className="main">{children}</main>
    </div>
  );
}
