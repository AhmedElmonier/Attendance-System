# Tasks: Phase 3 - Advanced Security & Mobile

**Input**: Design documents from `/specs/004-advanced-security-mobile/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

## Phase 1: Setup (Shared Infrastructure)
**Purpose**: Project initialization and basic structure

- [X] T001 Create project structure for new security modules in `cloud/`, `edge/`, and `mobile/`
- [X] T002 Initialize Flutter project in `mobile/` with `firebase_messaging`, `firebase_crashlytics`, and `riverpod`
- [ ] T002.1 Configure `firebase_crashlytics` for crash-free session tracking (SC-005)
- [X] T003 [P] Generate Ed25519 master keys for remote command signing

---

## Phase 2: Foundational (Blocking Prerequisites)
**Purpose**: Core security and communication layers required by all stories

- [X] T004 [P] Implement Ed25519 signing utility in `cloud/src/utils/signing.py`
- [X] T005 [P] Implement signature verification hook in `edge/src/utils/security.py`
- [X] T006 [P] Update `EncryptedDB` in `edge/src/storage/db.py` to support `PRAGMA secure_delete = ON`
- [X] T007 Implement base REST client for mobile in `mobile/lib/services/api_service.dart`

**Checkpoint**: Security foundation ready.

---

## Phase 3: User Story 1 - Remote Biometric Purge (Priority: P1) 🎯 MVP
**Goal**: Allow cloud admins to remotely and securely wipe kiosk biometric data.

**Independent Test**: Issue a signed wipe via MQTT/Admin API and verify `biometric_templates` table is empty and overwritten on the edge.

- [X] T008 [US1] Create `WipeCommand` model in `cloud/src/models/action.py`
- [X] T009 [US1] Implement Remote Wipe trigger endpoint in `cloud/src/api/admin_actions.py`
- [X] T010 [US1] Implement secure wipe execution logic in `edge/src/biometrics/wipe.py` (SQL + Index clear)
- [X] T011 [US1] Integrate wipe handler with MQTT listener in `edge/src/sync/mqtt_client.py`
- [X] T012 [US1] Add "Wipe Command" audit logging in cloud `audit_log` table

**Checkpoint**: US1 fully functional (MVP security feature).

---

## Phase 4: User Story 2 - Mobile Alert & Override (Priority: P1)
**Goal**: Manager push notifications and real-time event approval.

**Independent Test**: Mock a 0.65 confidence match; verify push arrives on mobile and "Approve" (with reason) updates record to "Present (Manual Override)".

- [X] T013 [P] [US2] Implement Mobile Device registration endpoint (`fcm_token`) in `cloud/src/api/mobile_mgmt.py`
- [X] T014 [US2] Implement Unverified Alerts feed endpoint in `cloud/src/api/mobile_mgmt.py`
- [X] T015 [US2] Implement Override processing logic with mandatory reason validation in `cloud/src/services/override.py`
- [X] T016 [P] [US2] Setup FCM background service in `mobile/lib/services/fcm_service.dart`
- [X] T017 [US2] Build Alerts Feed screen in `mobile/lib/screens/alerts_screen.dart`
- [X] T018 [US2] Build Manual Override dialog in `mobile/lib/screens/override_dialog.dart`

**Checkpoint**: US1 and US2 functional together.

---

## Phase 5: User Story 3 - Periocular Recognition Fallback (Priority: P2)
**Goal**: Recognition for users with face coverings (masks/niqabs).

**Independent Test**: Feed the vision pipeline an image with an obscured mouth; verify "Periocular Mode" triggers and matches eye region correctly.

- [X] T019 [US3] Implement eye-region ROI detection in `edge/src/vision/pose.py` using FaceMesh landmarks 133, 362
- [X] T020 [US3] Create ocular-specific crop service in `edge/src/vision/periocular.py`
- [X] T021 [US3] Update matching pipeline in `edge/src/biometrics/matcher.py` to handle ocular embeddings
- [X] T022 [US3] Add telemetry for "Fallback Triggered" events to monitor performance

---

## Phase 6: User Story 4 - High-Security Encrypted Backups (Priority: P2)
**Goal**: Daily AES-256 cloud backups.

- [X] T023 [US4] Implement backup encryption script (AES-256-GCM) in `cloud/src/services/backup.py`
- [X] T024 [US4] Configure scheduled backup job using `celery-beat` in `cloud/src/core/scheduler.py`
- [X] T025 [US4] Implement integrity check (HMAC/Sig) for backup retrieval in `cloud/src/services/backup.py`

---

## Phase 7: Polish & Cross-Cutting Concerns
- [X] T026 Implement multi-failure 60s lockout logic in `edge/src/biometrics/matcher.py`
- [X] T027 Add ID-entry fallback UI for kiosks in `edge/src/hal/display.py`
- [X] T028 Update `quickstart.md` with mobile app setup instructions
- [X] T029 Perform final end-to-end integration test of all Phase 3 features (including SC-004: <60s 1GB backup decryption)

---

## Dependencies & Execution Order
- **Setup -> Foundational**: Linear path.
- **US1 (Wipe)**: Requires Foundational; high priority (P1).
- **US2 (Mobile)**: Requires Foundational; high priority (P1).
- **US3 & US4**: Can proceed in parallel after Foundational.

## Implementation Strategy
- **Sprint 1 (MVP)**: Phase 1 -> Phase 2 -> Phase 3 (Remote Wipe).
- **Sprint 2**: Phase 4 (Mobile Alerts).
- **Sprint 3**: Phase 5 (Periocular) & Phase 6 (Backups).
