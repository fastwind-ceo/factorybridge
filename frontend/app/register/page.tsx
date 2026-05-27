'use client';

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

const roleConfig: Record<PortalRole, { label: string; companyType: string; redirect: string; badgeClass: string; title: string; description: string }> = {
  customer: {
    label: 'Customer / Buyer',
    companyType: 'CUSTOMER',
    redirect: '/customer',
    badgeClass: 'badge',
    title: 'Request production',
    description: 'Create RFQs and compare supplier quotes.',
  },
  supplier: {
    label: 'Supplier / Factory',
    companyType: 'SUPPLIER',
    redirect: '/supplier',
    badgeClass: 'badge green',
    title: 'Join tenders',
    description: 'Receive RFQs and submit structured quotations.',
  },
  operator: {
    label: 'Operator / Platform team',
    companyType: 'PLATFORM_OPERATOR',
    redirect: '/operator',
    badgeClass: 'badge amber',
    title: 'Manage platform',
    description: 'Moderate RFQs, suppliers and commercial readiness.',
  },
};

function saveAuthSession(payload: TokenResponse) {
  window.localStorage.setItem('factorybridge.access_token', payload.access_token);
  window.localStorage.setItem('factorybridge.refresh_token', payload.refresh_token);
  window.localStorage.setItem('factorybridge.user', JSON.stringify(payload.user));
}

function getErrorMessage(error: unknown) {
  return error instanceof Error ? error.message : 'Unexpected authentication error';
}

export default function RegisterPage() {
  const router = useRouter();
  const [role, setRole] = useState<PortalRole>('customer');
  const [companyName, setCompanyName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      const payload = await apiPost<TokenResponse>('/auth/register', {
        email,
        password,
        company_name: companyName,
        company_type: roleConfig[role].companyType,
      });

      saveAuthSession(payload);
      router.push(roleConfig[role].redirect);
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
        <div className="card" style={{ width: '100%', maxWidth: 760 }}>
          <div className="kicker">FactoryBridge onboarding</div>
          <h1>Create account</h1>
          <p>
            Choose a role, create your account and continue to the matching workspace. The selected role now controls the backend registration payload and redirect.
          </p>

          <form className="form" style={{ marginTop: 18 }} onSubmit={handleSubmit}>
            <div className="grid grid-2">
              <div className="field">
                <span className="label">Company role</span>
                <select className="select" value={role} onChange={(event) => setRole(event.target.value as PortalRole)}>
                  {Object.entries(roleConfig).map(([key, value]) => (
                    <option key={key} value={key}>{value.label}</option>
                  ))}
                </select>
              </div>

              <div className="field">
                <span className="label">Company name</span>
                <input className="input" value={companyName} onChange={(event) => setCompanyName(event.target.value)} placeholder="Example Manufacturing LLC" required minLength={2} />
              </div>

              <div className="field">
                <span className="label">Work email</span>
                <input className="input" type="email" value={email} onChange={(event) => setEmail(event.target.value)} placeholder="name@company.com" required />
              </div>

              <div className="field">
                <span className="label">Password</span>
                <input className="input" type="password" value={password} onChange={(event) => setPassword(event.target.value)} placeholder="Create secure password" required minLength={8} />
              </div>
            </div>

            {error ? (
              <div className="card" style={{ marginTop: 18, borderColor: '#fecaca', color: '#991b1b' }}>
                {error}
              </div>
            ) : null}

            <div className="grid grid-3" style={{ marginTop: 22 }}>
              {(Object.keys(roleConfig) as PortalRole[]).map((roleKey) => {
                const item = roleConfig[roleKey];
                const active = role === roleKey;

                return (
                  <button
                    key={roleKey}
                    type="button"
                    className="card role-card"
                    onClick={() => setRole(roleKey)}
                    style={{ textAlign: 'left', borderColor: active ? '#2563eb' : undefined, cursor: 'pointer' }}
                  >
                    <span className={item.badgeClass}>{item.label.split(' / ')[0]}</span>
                    <h2>{item.title}</h2>
                    <p>{item.description}</p>
                  </button>
                );
              })}
            </div>

            <div style={{ marginTop: 22, display: 'flex', gap: 12, alignItems: 'center', flexWrap: 'wrap' }}>
              <button className="btn" type="submit" disabled={isSubmitting}>
                {isSubmitting ? 'Creating account...' : `Create ${roleConfig[role].label} account`}
              </button>
              <span style={{ color: '#64748b' }}>Already registered? <a href="/login" style={{ color: '#1d4ed8', fontWeight: 700 }}>Sign in</a></span>
            </div>
          </form>
        </div>
      </section>
    </main>
  );
}
