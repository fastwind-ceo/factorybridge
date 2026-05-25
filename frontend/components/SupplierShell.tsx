import Link from 'next/link';
import type { ReactNode } from 'react';

const nav = [
  ['Supplier Dashboard', '/supplier'],
  ['Company Profile', '/supplier/profile'],
  ['Available RFQs', '/supplier/rfqs'],
  ['My Quotes', '/supplier/quotes'],
  ['Customer Portal', '/dashboard'],
];

export function SupplierShell({ children }: { children: ReactNode }) {
  return (
    <div className="shell">
      <aside className="sidebar">
        <Link href="/" className="logo">FactoryBridge <span>Supplier</span></Link>
        <nav className="nav">
          {nav.map(([label, href]) => <Link key={href} href={href}>{label}</Link>)}
        </nav>
      </aside>
      <main className="main">{children}</main>
    </div>
  );
}
