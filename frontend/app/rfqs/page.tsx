import Link from 'next/link';
import { AppShell } from '@/components/AppShell';
import { RFQTable } from '@/components/RFQTable';
export default function RFQListPage() { return <AppShell><div className="topbar"><div><div className="kicker">My RFQs</div><h1>Customer request pipeline</h1></div><Link className="btn" href="/rfqs/new">New RFQ</Link></div><div className="card"><RFQTable /></div></AppShell>; }
