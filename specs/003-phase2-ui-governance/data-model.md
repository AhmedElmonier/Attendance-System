# Data Model: Phase 2 - Bilingual UI/UX & Governance

## Edge Persistence (SQLite/SQLCipher)

### Employees (Enhanced)
| Column | Type | Description |
|--------|------|-------------|
| employee_id | UUID (PK) | Unique identifier |
| name_ar | TEXT | Arabic name |
| name_en | TEXT | English name |
| role | TEXT | User role (Manager/Staff) |
| status | TEXT | Active/Suspended/Pending |
| sync_status | TEXT | 'synced' / 'pending' |

---

## Cloud Persistence (PostgreSQL + RLS)

### approval_requests
| Column | Type | Description |
|--------|------|-------------|
| id | UUID (PK) | Request identifier |
| tenant_id | UUID (FK) | Scoped to tenant |
| entity_type | TEXT | 'EMPLOYEE', 'BIOMETRIC', 'SITE' |
| entity_id | UUID | Target record ID |
| change_payload | JSONB | The proposed data diff |
| maker_id | UUID (FK) | User who initiated the change |
| checker_id | UUID (FK) | User who approved/rejected |
| status | TEXT | 'PENDING', 'APPROVED', 'REJECTED' |
| reason | TEXT | Denial or approval reason |
| created_at | TIMESTAMP | |

### audit_logs
| Column | Type | Description |
|--------|------|-------------|
| id | UUID (PK) | |
| tenant_id | UUID (FK) | |
| actor_id | UUID (FK) | Who performed the action |
| action | TEXT | 'CREATE', 'UPDATE', 'DELETE', 'LOGIN' |
| entity_type | TEXT | |
| entity_id | UUID | |
| old_values | JSONB | State before change |
| new_values | JSONB | State after change |
| ip_address | TEXT | Client IPv4/IPv6 |
| timestamp | TIMESTAMP | |

### tenants (Enhanced)
| Column | Type | Description |
|--------|------|-------------|
| tenant_id | UUID (PK) | |
| allowed_ips | TEXT[] | Array of CIDR blocks (e.g., ['192.168.1.0/24']) |
| ip_restriction_enabled | BOOLEAN | Toggle for the security feature |
