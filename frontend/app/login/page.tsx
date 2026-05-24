export default function LoginPage() {
  return (
    <main className="container">
      <div className="card" style={{ maxWidth: 520, margin: '40px auto' }}>
        <h1>Login</h1>
        <p className="muted">Access customer, supplier and operator dashboards.</p>

        <div className="grid" style={{ marginTop: 24 }}>
          <input className="input" placeholder="Email" type="email" />
          <input className="input" placeholder="Password" type="password" />
          <button className="button">Sign in</button>
        </div>
      </div>
    </main>
  )
}
