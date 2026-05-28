'use client';

import Link from 'next/link';
import { FormEvent, useState } from 'react';
import { useRouter } from 'next/navigation';
import { PublicHeader } from '@/components/PublicHeader';
import { apiPost } from '@/lib/api';

type PortalRole = 'customer' | 'supplier' | 'operator';

type TokenResponse = {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: {
    id: string;
    email: string;
    roles: string[];
  };
};

type ApiResponse<T> = {
  success: boolean;
  data: T;
  message?: string | null;
};

const roleRedirect: Record<PortalRole, string> = {
  customer: '/customer',
  supplier: '/supplier',
  operator: '/admin',
};

const demoEmails: Record<PortalRole, string> = {
  customer: 'customer@factorybridge.demo',
  supplier: 'supplier@factorybridge.demo',
  operator: 'admin@factorybridge.demo',
};

function saveAuthSession(payload: TokenResponse) {
  window.localStorage.setItem('factorybridge.access_token', payload.access_token);
  window.localStorage.setItem('factorybridge.refresh_token', payload.refresh_token);
  window.localStorage.setItem('factorybridge.user', JSON.stringify(payload.user));
}

function unwrapApiData<T>(response: ApiResponse<T>): T {
  if (!response.success || !response.data) {
    throw new Error(response.message || 'Backend returned an unsuccessful response');
  }
  return response.data;
}

function preferredRoleFromToken(payload: TokenResponse, selectedRole: PortalRole): PortalRole {
  const roles = payload.user.roles.map((role) => role.toLowerCase());

  if (selectedRole === 'operator' && (roles.includes('operator') || roles.includes('admin'))) {
    return 'operator';
  }

  if (roles.includes(selectedRole)) {
    return selectedRole;
  }

  if (roles.includes('admin') || roles.includes('operator')) {
    return 'operator';
  }

  if (roles.includes('supplier')) {
    return 'supplier';
  }

  return 'customer';
}

function getErrorMessage(error: unknown) {
  return error instanceof Error ? error.message : 'Unexpected authentication error';
}

export default function LoginPage() {
  const router = useRouter();
  const [role, setRole] = useState<PortalRole>('customer');
  const [email, setEmail] = useState(demoEmails.customer);
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  function chooseDemoRole(nextRole: PortalRole) {
    setRole(nextRole);
    setEmail(demoEmails[nextRole]);
    setPassword('');
    setError(null);
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      const response = await apiPost<ApiResponse<TokenResponse>>('/auth/login', { email, password });
      const payload = unwrapApiData(response);
      saveAuthSession(payload);
      const targetRole = preferredRoleFromToken(payload, role);
      router.push(roleRedirect[targetRole]);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="page public-page">
      <PublicHeader />

      <section style={{ display: 'grid', placeItems: 'center', padding: '40px 0' }}>
        <div className="card" style={{ width: '100%', maxWidth: 560 }}>
          <div className="kicker">FactoryBridge access</div>
          <h1>Sign in</h1>

          <p>
            Sign in through the live backend API. The selected portal is used as the preferred redirect, while backend roles remain the source of truth.
          </p>

          <form className="form" style={{ marginTop: 18 }} onSubmit={handleSubmit}>
            <div className="field">
              <span className="label">Preferred portal</span>
              <select className="select" value={role} onChange={(event) => chooseDemoRole(event.target.value as PortalRole)}>
                <option value="customer">Customer</option>
                <option value="supplier">Supplier</option>
                <option value="operator">Operator/Admin</option>
              </select>
            </div>

            <div className="field">
              <span className="label">Email</span>
              <input className="input" type="email" value={email} onChange={(event) => setEmail(event.target.value)} required />
            </div>

            <div className="field">
              <span className="label">Password</span>
              <input className="input" type="password" value={password} onChange={(event) => setPassword(event.target.value)} required autoComplete="current-password" />
            </div>

            {error ? (
              <div className="card" style={{ borderColor: '#fecaca', color: '#991b1b' }}>
                {error}
              </div>
            ) : null}

            <div className="grid grid-3">
              <button type="button" className="btn" onClick={() => chooseDemoRole('customer')}>Customer demo</button>
              <button type="button" className="btn secondary" onClick={() => chooseDemoRole('supplier')}>Supplier demo</button>
              <button type="button" className="btn ghost" onClick={() => chooseDemoRole('operator')}>Admin demo</button>
            </div>

            <button className="btn" type="submit" disabled={isSubmitting}>
              {isSubmitting ? 'Signing in...' : `Sign in to ${role}`}
            </button>
          </form>

          <div className="card" style={{ marginTop: 18, background: '#f8fafc' }}>
            <strong>Demo accounts</strong>
            <p style={{ margin: '8px 0 0' }}>Use a demo email button above and enter the staging demo password from the deployment checklist.</p>
          </div>

          <p style={{ marginTop: 18 }}>
            No account? <Link href="/register" style={{ color: '#1d4ed8', fontWeight: 700 }}>Register</Link>
          </p>
        </div>
      </section>
    </main>
  );
}
