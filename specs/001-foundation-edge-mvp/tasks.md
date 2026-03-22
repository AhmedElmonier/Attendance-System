# Implementation Tasks: Foundation & Edge MVP (Phase 1)

**Feature**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md) | **Branch**: `001-foundation-edge-mvp`

## Phase 1: Setup

- [x] T001 Initialize project structure for `edge/` and `cloud/` directories per plan.md
- [x] T002 Create `requirements.txt` with core dependencies (opencv-python, mediapipe, pytorch, hnswlib, fastapi, sqlalchemy)
- [x] T003 [P] Set up Python virtual environment and install dependencies in root directory

## Phase 2: Foundational (Platform & Storage)

- [x] T004 Implement Hardware Abstraction Layer (HAL) for camera access in `edge/src/hal/camera.py` (Laptop/WSL2 focus)
- [x] T005 [P] Implement encrypted SQLite database manager (SQLCipher) in `edge/src/storage/db.py`
- [x] T006 [P] Initialize PostgreSQL database with multi-tenant schema in `cloud/src/db/schema.sql` (Cloud side)

## Phase 3: User Story 1 - Biometric Enrollment (P1)

**Goal**: Guide user through 5-pose capture and store encrypted biometric vectors locally.
**Independent Test**: Run `python edge/src/main.py --mode enroll`, follow prompts, and verify vector exists in `biometric_templates` table.

- [x] T007 [P] [US1] Implement head pose (Yaw/Pitch) detection in `edge/src/vision/pose.py` using MediaPipe
- [x] T008 [US1] Implement 5-pose guided capture logic (Center, L, R, U, D) in `edge/src/vision/enrollment.py`
- [x] T009 [P] [US1] Setup MobileFaceNet embedding extraction pipeline in `edge/src/biometrics/embeddings.py`
- [x] T010 [US1] Implement local HNSW indexing for templates in `edge/src/biometrics/index.py`
- [x] T011 [US1] Integrate enrollment flow into main CLI in `edge/src/main.py`

## Phase 4: User Story 2 - Offline Attendance Clock-In (P1)

**Goal**: Real-time face matching and local logging without network dependency.
**Independent Test**: Perform a matching attempt on an enrolled user with network disabled; verify "Identity Confirmed" and SQLite log entry.

- [x] T012 [P] [US2] Implement sub-200ms vector matching logic using hnswlib in `edge/src/biometrics/matcher.py`
- [x] T013 [US2] Implement real-time "Primary Face" identification (centered/largest) in `edge/src/vision/scene.py`
- [x] T014 [US2] Implement offline logging to SQLite with JSON metadata in `edge/src/storage/logger.py`
- [x] T015 [US2] Integrate clock-in flow into main CLI in `edge/src/main.py`

## Phase 5: User Story 3 - Batch Synchronization (P2)

**Goal**: Secure, chunked upload of local logs once connectivity is restored.
**Independent Test**: Reconnect network and verify logs are moved from SQLite `pending` status to PostgreSQL `attendance_events`.

- [x] T016 [P] [US3] Implement chunked sync batcher (500 logs) in `edge/src/sync/batcher.py`
- [x] T017 [US3] Implement FastAPI sync endpoint (`POST /api/v1/sync/attendance`) in `cloud/src/api/sync.py`
- [x] T018 [P] [US3] Implement SHA-256 integrity verification and NTP drift check in `cloud/src/core/security.py`
- [x] T019 [US3] Implement network monitoring and auto-trigger for sync in `edge/src/sync/monitor.py`

## Phase 6: Polish & Cross-Cutting

- [x] T020 Implement localized (AR/EN) text/audio feedback module in `edge/src/hal/feedback.py`
- [x] T021 Perform end-to-end integration test: Enroll -> Clock-in (Offline) -> Sync -> Cloud Verification

## Dependencies & Parallelism

**Execution Order**: Phase 1 -> Phase 2 -> Phase 3 -> Phase 4 -> Phase 5 -> Phase 6.

**Parallel Opportunities**:
- T003, T005, T006 (Setup/Storage)
- T007, T009 (Vision/Biometrics within US1)
- T012, T016 (Matching/Sync development)

**MVP Scope**: Phase 1 through Phase 4 (Enrollment + Local Clock-in).
