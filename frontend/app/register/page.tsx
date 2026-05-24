export default function RegisterPage() {
  return (
    <main className="container">
      <div className="card" style={{ maxWidth: 640, margin: '40px auto' }}>
        <h1>Create account</h1>
        <p className="muted">Register as customer or supplier company.</p>

        <div className="grid" style={{ marginTop: 24 }}>
          <input className="input" placeholder="Company name" />
          <select className="input" defaultValue="CUSTOMER">
            <option value="CUSTOMER">Customer</option>
            <option value="SUPPLIER">Supplier</option>
          </select>
          <input className="input" placeholder="Email" type="email" />
          <input className="input" placeholder="Password" type="password" />
          <button className="button">Create account</button>
        </div>
      </div>
    </main>
  )
}
