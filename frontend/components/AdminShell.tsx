import Link from 'next/link';
import type { ReactNode } from 'react';

const nav = [
  ['Operator Dashboard', '/admin'],
  ['RFQ Moderation', '/admin/rfqs'],
  ['Supplier Verification', '/admin/suppliers'],
  ['Tender Control', '/admin/tenders'],
  ['Quote Review', '/admin/quotes'],
  ['Landed Cost Builder', '/admin/landed-costs'],
  ['Audit Logs', '/admin/audit'],
  ['Customer Portal', '/dashboard'],
  ['Supplier Portal', '/supplier'],
];

export function AdminShell({ children }: { children: ReactNode }) {
  return (
    <div className="shell">
      <aside className="sidebar">
        <Link href="/" className="logo">FactoryBridge <span>Operator</span></Link>
        <nav className="nav">
          {nav.map(([label, href]) => <Link key={href} href={href}>{label}</Link>)}
        </nav>
      </aside>
      <main className="main">{children}</main>
    </div>
  );
}
