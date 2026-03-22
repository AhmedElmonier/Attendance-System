# Data Model: Foundation & Edge (Phase 1)

## Edge Persistence (SQLite)

### Table: `employees`
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | Primary Key | Global Employee ID |
| `name_ar` | TEXT | Not Null | Arabic Name |
| `name_en` | TEXT | Not Null | English Name |
| `status` | TEXT | Default 'active' | active, suspended |

### Table: `biometric_templates`
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | INTEGER | Primary Key | Local HNSW Label |
| `employee_id` | UUID | Foreign Key | Mapping to employee |
| `vector_blob` | BLOB | Not Null | Encrypted 512-d embedding |
| `pose` | TEXT | Not Null | center, left, right, up, down |

### Table: `attendance_logs`
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | Primary Key | Event ID |
| `employee_id` | UUID | Foreign Key | The person who clocked in |
| `timestamp` | DATETIME | Default CURRENT_TIMESTAMP | Event time (UTC) |
| `confidence` | FLOAT | 0.0 - 1.0 | Matching confidence score |
| `sync_status` | TEXT | Default 'pending' | pending, synced, failed |

---

## Cloud Persistence (PostgreSQL)

The cloud schema mirrors the edge tables but adds multi-tenant scoping and integrity headers.

### Table: `attendance_events` (Scoped)
- `id`: UUID (Primary Key)
- `tenant_id`: UUID (RLS partitioned)
- `employee_id`: UUID
- `timestamp`: TIMESTAMPTZ
- `device_id`: TEXT
- `integrity_hash`: TEXT (SHA-256 of payload)
