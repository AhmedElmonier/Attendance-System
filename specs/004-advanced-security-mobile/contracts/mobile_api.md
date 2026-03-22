# Mobile API Contracts (Phase 3)

## Base URL: `/api/v1/mobile`

### 1. Device Registration
`POST /register`
Registers a mobile device for push notifications.

**Payload**:
```json
{
  "fcm_token": "string",
  "os_type": "android|ios",
  "device_name": "string"
}
```
**Response**: `200 OK`

---

### 2. Fetch Unverified Alerts
`GET /alerts`
Returns a list of unverified attendance events requiring manager review.

**Query Params**: `site_id` (optional), `limit` (default 50)

**Response**:
```json
[
  {
    "event_id": "uuid",
    "employee_id": "uuid",
    "employee_name": "string",
    "timestamp": "iso8601",
    "confidence": 0.76,
    "photo_url": "https://..."
  }
]
```

---

### 3. Process Override
`POST /override`
Approve or Reject an unverified attendance event.

**Payload**:
```json
{
  "event_id": "uuid",
  "action": "approve|reject",
  "reason": "string (mandatory for approve)"
}
```
**Response**: `200 OK`
