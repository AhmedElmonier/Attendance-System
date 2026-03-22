# Quickstart: Phase 2 - Bilingual Dashboard & Governance

## 1. Dashboard i18n Setup (Next.js)

1. **Install Dependencies**:
   ```bash
   npm install next-intl
   ```
2. **Configure Locales**:
   Add `messages/en.json` and `messages/ar.json`.
3. **RTL Support**:
   Ensure `layout.tsx` detects the locale and applies `dir="rtl"` to the HTML tag. Use Tailwind logical classes (`ps-`, `pe-`, `start-0`) instead of physical ones (`pl-`, `pr-`).

## 2. Kiosk Audio Engine (Python)

1. **Install Dependencies**:
   ```bash
   pip install pygame
   ```
2. **Asset Directory**:
   Place audio files in `edge/assets/audio/`.
   - `success_ar.wav`, `success_en.wav`
   - `look_camera_ar.wav`, `look_camera_en.wav`

## 3. Database Migrations (Cloud)

1. Run the migration scripts for `approval_requests` and `audit_logs` tables.
2. Enable RLS on the new tables:
   ```sql
   ALTER TABLE approval_requests ENABLE ROW LEVEL SECURITY;
   CREATE POLICY tenant_isolation ON approval_requests USING (tenant_id = current_setting('app.current_tenant')::uuid);
   ```
