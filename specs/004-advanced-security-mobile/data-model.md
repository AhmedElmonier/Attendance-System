# Data Model Design: Phase 3 Advanced Security & Mobile

## New Entities

### MobileDevice
- **id**: `UUID` (Primary Key)
- **tenant_id**: `UUID` (Foreign Key -> tenants)
- **user_id**: `UUID` (Foreign Key -> users/managers)
- **fcm_token**: `String` (Unique identifier for push notifications)
- **os_type**: `String` ('android' | 'ios')
- **last_active**: `DateTime`
- **is_active**: `Boolean` (Default: True)

### RemoteAction (Wipe Logging)
- **id**: `UUID` (Primary Key)
- **kiosk_id**: `String` (Target device)
- **action_type**: `String` ('WIPE_FULL')
- **signed_payload**: `Text` (The base64 encoded Ed25519 payload)
- **issued_by**: `UUID` (Admin user ID)
- **issued_at**: `DateTime`
- **status**: `String` ('PENDING', 'SENT', 'VERIFIED', 'FAILED')

### BackupLog
- **id**: `UUID` (Primary Key)
- **artifact_path**: `String` (Path in cloud storage)
- **checksum**: `String` (SHA-256)
- **encryption_version**: `String` (e.g., '1.0-aes-256-gcm')
- **created_at**: `DateTime`
- **size_bytes**: `BigInt`

## Modified Entities

### AttendanceLog (Cloud/Edge)
- **review_reason**: `Text` (Mandatory if `status` is 'Present (Manual Override)')
- **reviewed_by**: `UUID` (Manager ID who approved)
- **reviewed_at**: `DateTime`
- **lockout_metadata**: `JSONB` (Optional: stores failure count, timestamps for local lockout logic)

## State Transitions
1. **Wipe Workflow**: `PENDING` -> `SENT` (via MQTT) -> `VERIFIED` (Kiosk feedback loop).
2. **Attendance Review**: `Unverified` -> `Present (Manual Override)` (Requires Reason + Manager ID).
