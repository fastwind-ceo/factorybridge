import Link from 'next/link';
import { AppShell } from '@/components/AppShell';
import { MetricCard } from '@/components/MetricCard';
import { RFQTable } from '@/components/RFQTable';

export default function DashboardPage() {
  return <AppShell><div className="topbar"><div><div className="kicker">Customer dashboard</div><h1>Manufacturing RFQs</h1><p>Control customer requests, AI review status, supplier quotes and landed-cost progress.</p></div><Link className="btn" href="/rfqs/new">Create RFQ</Link></div><section className="grid grid-4"><MetricCard label="Draft RFQs" value="2" /><MetricCard label="AI reviewed" value="4" /><MetricCard label="Quotes received" value="7" /><MetricCard label="Active orders" value="1" /></section><section className="card" style={{ marginTop: 22 }}><h2>Recent RFQs</h2><RFQTable /></section></AppShell>;
}
