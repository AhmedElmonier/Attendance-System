# Feature Specification: Phase 2 - Bilingual UI/UX & Governance

**Feature Branch**: `003-phase2-ui-governance`  
**Created**: 2026-03-22  
**Status**: Draft  
**Input**: User description: "create specification for phase 2 Phase 2: Bilingual UI/UX & Governance using best practices"

## Clarifications

### Session 2026-03-22
- Q: Can a user who holds both Manager and Admin roles approve their own submitted requests (Self-Approval)? → A: Restricted (Strict) - Self-approval is never allowed; a different Admin must always perform the check.
- Q: How should a kiosk behave if an employee's biometric template has been updated in the Cloud, but the device hasn't finished download it? → A: Hybrid - Allow matching against the old local template with a high-confidence threshold (>=98%); flag event as "Stale Template" in logs.
- Q: Should the audio system provide active guidance during the facial capture process or only signal the final outcome? → A: Smart Guidance - Audio prompts for guidance trigger only if the user is in the frame for >3 seconds without a successful capture.
- Q: What level of detail should the "Diff View" provide for biometric template updates in the Approvals Inbox? → A: Visual - Display side-by-side reference photos (old vs new) for Admin verification.
- Q: Should the system restrict administrative dashboard access to specific IP ranges (allow-listing)? → A: Allow-listing (Optional) - Support optional, organization-configurable IP allow-listing for Admin accounts.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Bilingual Management Dashboard (Priority: P1)

As a Branch Manager in Egypt, I want to toggle the management dashboard between Arabic and English so that I can manage my site using my native language with proper Right-to-Left (RTL) mirroring.

**Why this priority**: Essential for local market adoption and operational efficiency for non-English speaking managers.

**Independent Test**: Can be tested by navigating to the dashboard and clicking the language switcher; verify all components (sidebar, navigation, content) mirror correctly and text is translated.

**Acceptance Scenarios**:

1. **Given** the manager is on the English dashboard, **When** they select "Arabic", **Then** the sidebar moves to the right, the main content moves to the left, and all UI text is displayed in Arabic.
2. **Given** a data table, **When** in Arabic mode, **Then** text aligns to the right and punctuation/icons adapt to the RTL flow.

---

### User Story 2 - "Maker-Checker" Approval Workflow (Priority: P1)

As a System Admin, I want to ensure that any change to an employee's biometric profile (re-enrollment or deletion) requires a second approval so that we prevent unauthorized tampering with attendance data.

**Why this priority**: Critical for governance and preventing internal fraud (e.g., "ghost" employees or unauthorized enrollment).

**Independent Test**: Can be tested by initiating an employee record deletion as a Manager and verifying it remains in a "Pending Approval" state until an Admin reviews it.

**Acceptance Scenarios**:

1. **Given** a Manager requests to delete an employee, **When** the request is submitted, **Then** the employee record is NOT deleted, and a record appears in the "Approvals Inbox".
2. **Given** an Admin is in the "Approvals Inbox", **When** they review a request they created themselves, **Then** the "Approve" button is disabled/hidden to prevent self-approval.
3. **Given** an Admin reviews a biometric update, **When** they view the request, **Then** the system MUST display a "Side-by-Side" visual comparison of the reference photos from the old and new enrollments.
4. **Given** an Admin is in the "Approvals Inbox", **When** they approve a request from a different Maker, **Then** the action is performed and logged.

---

### User Story 3 - Edge Kiosk RTL UI & Localized Audio (Priority: P2)

As an Employee, I want the edge kiosk to display instructions in my preferred language and play audio feedback so that I am certain my biometric scan was successful without needing assistance.

**Why this priority**: Improves throughput during peak clock-in times and ensures inclusivity.

**Independent Test**: Can be tested on the edge simulator by switching the "Locale" configuration and verifying the on-screen text and simulated audio output match the selection.

**Acceptance Scenarios**:

1. **Given** the kiosk is set to Arabic, **When** no face is detected, **Then** the screen displays "Please look at the camera / الرجاء النظر إلى الكاميرا" in a centered, RTL-compatible layout.
2. **Given** a successful attendance match, **When** the event is recorded, **Then** the kiosk plays a "Success / تم تأكيد الحضور" audio prompt.
3. **Given** a user is facing the camera, **When** no match is found for >3 seconds, **Then** the kiosk initiates smart audio guidance (e.g., "Move closer / اقترب قليلاً").

---

### User Story 4 - Audit Trail & Governance Logging (Priority: P2)

As a Compliance Officer, I want to see a detailed history of all administrative actions so that I can investigate discrepancies or unauthorized changes.

**Why this priority**: Ensures accountability and satisfies enterprise auditing requirements.

**Independent Test**: Can be tested by performing several manager actions (edit, delete, login) and verifying they appear in the "Audit Logs" section with correct timestamps and actor IDs.

**Acceptance Scenarios**:

1. **Given** an administrative action is performed, **When** viewed in the Audit Log, **Then** it must include who did it, what changed (old vs new), and the direct IP/device ID.

---

### Edge Cases

- **Partial Sync during Approvals**: What happens if a "Pending Approval" change is made while the kiosk is offline? (Resolved: Approval logic lives in the Cloud; edge kiosks only pull "Approved" states during their heartbeat. If a local template is marked for update but the new one isn't downloaded, the system uses "Hybrid Matching" logic).
- **Simultaneous Edits**: Two managers edit the same employee. (Resolved: The "Maker" request captures the original hash; if the hash changed before approval, the request is invalidated).
- **Missing Audio Assets**: Kiosk cannot find an audio file. (Resolved: System falls back to visual-only feedback and logs a local warning).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Dashboard MUST implement `next-intl` (or equivalent) for AR/EN switching with CSS logical properties for layout mirroring.
- **FR-002**: System MUST store employee names in both `name_ar` and `name_en` fields.
- **FR-003**: System MUST provide a "Maker-Checker" state machine for sensitive edits (Biometrics, Termination, Site Transfers).
- **FR-004**: The system MUST strictly prohibit "Self-Approval"; any administrative change must be approved by a different user than the one who initiated it.
- **FR-005**: Edge devices MUST pull a "Verified State" from the Cloud and only apply changes that have been "Approved".
- **FR-006**: During template transitions (Cloud approved, Edge not yet downloaded), the Edge device MUST use a high-confidence threshold (>=98%) for the old template; events matching with <98% must be rejected as "Update Required".
- **FR-007**: Kiosk MUST support localized audio output (pre-recorded wav/mp3) for successful/failed attendance events.
- **FR-008**: Audio guidance prompts MUST only trigger if a user remains in the camera frame for >3 seconds without a successful capture (Smart Guidance).
- **FR-009**: The "Approvals Inbox" MUST provide a side-by-side visual comparison (using reference photos) for all biometric template updates.
- **FR-010**: System MUST maintain an immutable Audit Log of all dashboard and API interactions.
- **FR-011**: System MUST support optional IP allow-listing per organization for all administrative (Admin/Manager) accounts.

### Key Entities *(include if feature involves data)*

- **ApprovalRequest**: Tracks the lifecycle of a sensitive change (Draft -> Pending -> Approved/Rejected).
- **AuditLog**: Sequential record of all system state changes.
- **SiteManager**: Role with scoped access to specific site data and "Maker" permissions.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of dashboard UI strings MUST be localized in both Arabic and English.
- **SC-002**: Audit logs MUST be searchable and exportable within < 1 second for a 30-day window.
- **SC-003**: UI components MUST have zero layout breaks when toggled from LTR to RTL.
- **SC-004**: Attendance feedback (visual/audio) MUST trigger within < 100ms of recognition on the edge device.
- **SC-005**: 100% of administrative login attempts from non-allowlisted IPs MUST be rejected with a 403 Forbidden error if the feature is enabled.

## Assumptions & Dependencies

- **A-001**: Cloud storage for pre-recorded audio files will be served to edge devices during provisioning.
- **A-002**: Localized audio prompts will be pre-stored on the edge SD card/storage to avoid playback latency.
- **D-001**: Depends on Phase 1 "Sync API" for state reconciliation.
