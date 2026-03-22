# API Contracts: Phase 2 - Governance & Reporting

## 1. Approval Requests

### `GET /api/v1/governance/approvals`
- **Description**: List all pending/history approval requests for the tenant.
- **Role**: Admin, Manager (Filtered to site).
- **Query Params**: `status` (PENDING/APPROVED/REJECTED), `entity_type`.

### `POST /api/v1/governance/approvals/{id}/action`
- **Description**: Approve or Reject a pending request.
- **Request Body**:
```json
{
  "action": "APPROVED",
  "reason": "Verified identity via visual match."
}
```
- **Constraint**: `checker_id` MUST NOT equal `maker_id`. Returns `403 FORBIDDEN` on self-approval.

---

## 2. Audit Logs

### `GET /api/v1/governance/audit-logs`
- **Description**: Search system audit history.
- **Query Params**: `actor_id`, `start_date`, `end_date`, `entity_id`.
- **Performance**: Must utilize index on `(tenant_id, timestamp)` for < 1s retrieval.

---

## 3. Bilingual Entity Management

### `PATCH /api/v1/employees/{id}`
- **Description**: Update employee profile (initiates Maker-Checker if biometric/status change).
- **Request Body**:
```json
{
  "name_ar": "محمد علي",
  "name_en": "Mohamed Ali",
  "template_update": { ... } // Optional
}
```
