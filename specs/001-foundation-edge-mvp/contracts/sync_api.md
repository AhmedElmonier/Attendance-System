# Contract: Synchronization API (v1)

## Endpoint: `POST /api/v1/sync/attendance`

### Request Header
- `Authorization`: `Bearer <Device_X509_Signed_JWT>`
- `X-Device-ID`: Unique identifier of the kiosk/laptop
- `Content-Type`: `application/json`

### Request Body (JSON)
```json
{
  "batch_id": "uuid-v4",
  "kiosk_timestamp": "2026-03-22T15:30:00Z",
  "events": [
    {
      "event_id": "uuid-v4",
      "employee_id": "uuid-v4",
      "timestamp": "2026-03-22T15:25:00Z",
      "confidence": 0.982,
      "integrity_hash": "sha256-string"
    }
  ]
}
```

### Success Response (200 OK)
```json
{
  "status": "success",
  "synced_count": 1,
  "server_time": "2026-03-22T15:30:01Z"
}
```

### Error Responses
- **401 Unauthorized**: Invalid device certificate or expired JWT.
- **403 Forbidden**: Tenant isolation violation (RLS).
- **400 Bad Request**: NTP Drift too large ($\pm 5$ mins) or invalid `integrity_hash`.
