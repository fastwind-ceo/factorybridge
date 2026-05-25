# FactoryBridge Security Readiness Matrix

| Security Area | MVP Control | Status | Notes |
|---|---|---:|---|
| Authentication | JWT access tokens | PASS | Refresh token flow exists in auth layer design; MVP uses token flow in API tests. |
| Password storage | Hashing via password service | PASS | No plaintext password storage. |
| RBAC | Role checks on protected endpoints | PASS | ADMIN/OPERATOR/CUSTOMER/SUPPLIER enforced. |
| RFQ visibility | Owner/operator/admin/invited supplier | PASS | Supplier access is invitation-based. |
| File access | Per-file access level + signed download URL | PASS | Direct file ID guessing is blocked. |
| Quote confidentiality | Supplier cannot see competitor quotes | PASS | Customer comparison is safe view. |
| Internal margin protection | Customer-safe landed cost view | PASS | Internal margin fields hidden. |
| Audit | Critical action audit log | PASS | Login/RFQ/file/quote/cost/order events logged. |
| Notifications | Role/company notifications | PASS | Used for workflow visibility. |
| HTTPS | Nginx/SSL planned in deployment step | PENDING STEP 018 | Production hardening item. |
| Backup | Scripts planned in deployment step | PENDING STEP 018 | Production hardening item. |
| Watermarking | Not in MVP | FUTURE | Planned for confidential drawings. |
| 2FA | Not in MVP | FUTURE | Recommended for admin/operator accounts. |
| External KYC/sanctions screening | Manual MVP | FUTURE | Add vendor/API later. |
