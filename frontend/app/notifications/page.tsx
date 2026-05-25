import { AppShell } from '@/components/AppShell';
import { notifications } from '@/lib/mockData';
export default function NotificationsPage() { return <AppShell><div className="topbar"><div><div className="kicker">Notifications</div><h1>Operational updates</h1></div><button className="btn secondary">Mark all read</button></div><div className="grid">{notifications.map((n) => <div className="card" key={n.id}><strong>{n.title}</strong><p>{n.body}</p></div>)}</div></AppShell>; }
