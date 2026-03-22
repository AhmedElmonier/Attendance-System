# Tasks: Phase 2 - Bilingual UI/UX & Governance

**Input**: Design documents from `/specs/003-phase2-ui-governance/`
**Prerequisites**: plan.md, spec.md, data-model.md, contracts/governance_api.md

## Phase 1: Setup (Shared Infrastructure)

- [x] T001 [P] Initialize `next-intl` and configure middleware in `dashboard/src/middleware.ts`
- [x] T002 [P] Setup `pygame` dependencies and create `edge/assets/audio/` directory
- [x] T003 [P] Create initial `en.json` and `ar.json` translation files in `dashboard/messages/`

---

## Phase 2: Foundational (Blocking Prerequisites)

- [x] T004 Implement `ApprovalRequest` and `AuditLog` SQLAlchemy models in `cloud/src/models/governance.py`
- [x] T005 [P] Implement `IPFilterMiddleware` for CIDR allow-listing in `cloud/src/api/middleware/ip_filter.py`
- [x] T006 Setup base governance API routes and Pydantic schemas in `cloud/src/api/governance.py`
- [x] T007 Create database migrations for governance tables in `cloud/migrations/`
- [x] T027 [P] Create PostgreSQL index on `(tenant_id, timestamp)` for audit log performance (SC-002)

---

## Phase 3: User Story 1 - Bilingual Dashboard (Priority: P1) 🎯 MVP

**Goal**: Full RTL/LTR toggle support on the dashboard with localized strings.

**Independent Test**: Use the language switcher to toggle to Arabic; verify `dir="rtl"` on the body and that sidebar/content mirror correctly.

- [x] T008 [US1] Implement `LanguageSwitcher` component in `dashboard/src/components/i18n/LanguageSwitcher.tsx`
- [x] T009 [US1] Update `dashboard/src/layout.tsx` to handle locale-based layout mirroring (RTL)
- [x] T010 [US1] [P] Localize 'Employees', 'Approvals', and 'Audit' keys in `dashboard/messages/`
- [x] T011 [US1] Add Playwright E2E test for locale switching in `dashboard/tests/e2e/test_i18n.spec.ts`

---

## Phase 4: User Story 2 - "Maker-Checker" Approval Workflow (Priority: P1)

**Goal**: Sensitive edits (biometrics/deletion) require dual-person approval.

**Independent Test**: Submit a deletion request as a Manager; verify it appears in "Pending" and cannot be approved by the same user.

- [x] T012 [US2] Implement `ApprovalService` to intercept sensitive writes in `cloud/src/services/approval_service.py`
- [x] T013 [US2] Implement Approve/Reject logic with self-approval blocking in `cloud/src/api/governance.py`
- [x] T014 [US2] Create "Approvals Inbox" UI with status filtering in `dashboard/src/pages/approvals/index.tsx`
- [x] T015 [US2] [P] Implement side-by-side visual diff (photo compare) in `dashboard/src/components/governance/DiffViewer.tsx`
- [x] T016 [US2] Add integration test for the full Maker-Checker cycle in `cloud/tests/integration/test_governance.py`

---

## Phase 5: User Story 3 - Edge Kiosk RTL UI & Localized Audio (Priority: P2)

**Goal**: Offline kiosk feedback with Arabic voice prompts and smart guidance.

**Independent Test**: Use the edge simulator; verify that audio triggers on capture and "Smart Guidance" plays after 3s delay.

- [x] T017 [US3] Implement `AudioEngine` using `pygame.mixer` in `edge/src/audio/engine.py`
- [x] T018 [US3] Add 3-second smart guidance timer to the vision loop in `edge/src/vision/capture_loop.py`
- [x] T019 [US3] [P] Implement RTL-mirrored Kiosk UI layout in `edge/src/ui/main_window.py`
- [x] T020 [US3] Create audio playback validation script in `edge/tests/simulate_audio.py`
- [x] T026 [US3] Implement 98% confidence threshold logic for stale templates in edge matching loop (FR-006)

---

## Phase 6: User Story 4 - Audit Trail & Governance Logging (Priority: P2)

**Goal**: Immutable history of all administrative actions.

**Independent Test**: Perform a profile edit and verify an entry exists in the Audit Log with IP and actor details.

- [x] T021 [US4] Implement `@audit_log` decorator for FastAPI endpoints in `cloud/src/utils/audit.py`
- [x] T022 [US4] Create Audit Log viewer page with Date/Actor filters in `dashboard/src/pages/audit/index.tsx`

---

## Phase 7: Polish & Cross-Cutting Concerns

- [x] T023 [P] Implement IP Allow-listing settings UI in `dashboard/src/pages/settings/security.tsx`
- [x] T024 [P] Finalize AR/EN translation coverage for all tooltips in `dashboard/messages/`
- [x] T025 Run `quickstart.md` validation on clean environment

---

## Dependencies & Execution Order

1. **Foundational (Phase 2)** must be completed before any User Story implementation.
2. **User Stories 1 & 2** are Priority 1 and can be worked on in parallel after Phase 2.
3. **User Story 3** depends on User Story 1 (Locale infrastructure).
4. **User Story 4** depends on Foundational (Phase 2) logging schemas.
