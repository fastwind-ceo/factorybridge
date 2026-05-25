# FactoryBridge Production Readiness Checklist

## Application
- [x] Backend health endpoint works.
- [x] Auth flow works.
- [x] Customer RFQ flow works.
- [x] Supplier invitation and quote flow works.
- [x] Landed cost flow works.
- [x] Order MVP flow works.
- [x] Notifications work.
- [x] Audit logs work.
- [x] Security hardening tests pass.

## Security
- [x] Customer cannot access another customer's RFQ.
- [x] Supplier cannot access uninvited RFQ.
- [x] Supplier cannot access protected files without correct access level.
- [x] Supplier cannot see competitor quote data.
- [x] Customer cannot see internal quote fields.
- [x] Customer cannot see supplier/operator-only landed cost internals.
- [ ] HTTPS enabled on production domain.
- [ ] Production secrets moved to server-only `.env`.
- [ ] Firewall configured.

## Infrastructure
- [x] Docker structure exists.
- [x] Dev compose exists.
- [ ] Production compose finalized.
- [ ] Nginx production config finalized.
- [ ] SSL/Let's Encrypt guide finalized.
- [ ] Backup scripts finalized.

## Launch
- [ ] Production domain configured.
- [ ] Admin user created.
- [ ] Demo customer/supplier/operator seed verified.
- [ ] Pilot RFQ created.
- [ ] First supplier pool imported.
