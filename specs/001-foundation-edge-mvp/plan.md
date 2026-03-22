# Implementation Plan: Foundation & Edge MVP (Phase 1)

**Branch**: `001-foundation-edge-mvp` | **Date**: 2026-03-22 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/001-foundation-edge-mvp/spec.md`

## Summary
Implementation of the core biometric pipeline and edge infrastructure. This includes multi-angle face capture, HNSW-based local vector matching, and a robust offline-first synchronization engine using an encrypted SQLite database.

## Technical Context

**Language/Version**: Python 3.9+  
**Primary Dependencies**: 
- Vision: `opencv-python`, `mediapipe` (Face Mesh)
- AI/Biometrics: `pytorch` or `onnxruntime`, `hnswlib`
- Backend: `fastapi`, `sqlalchemy`, `pydantic`
- Sync: `awsiotsdk` (MQTT), `httpx` (HTTPS)
**Storage**: SQLite with SQLCipher (Edge), PostgreSQL (Cloud)  
**Testing**: `pytest` for core logic and sync serialization  
**Target Platform**: Laptop/WSL2 (Evaluation), Raspberry Pi 4 (Production target)
**Project Type**: Edge-to-Cloud Distributed System  
**Performance Goals**: $< 200\text{ms}$ biometric matching latency (on-device)  
**Constraints**: 30-day offline buffer, 512-dimension vector limit, no raw image persistence  
**Scale/Scope**: Initial MVP for 1k users across 10-50 kiosks

## Constitution Check

*GATE: Must pass before Phase 1 design.*

- **Privacy & Compliance**: System only stores 512-d feature vectors. No raw images. ✅
- **Edge-First Resilience**: Matching logic is entirely local using `hnswlib`. ✅
- **Bilingual UX**: Camera UI will provide localized AR/EN audio/text feedback. ✅
- **Hardware Abstraction (HAL)**: Vision and I/O logic will be behind a HAL for Laptop/WSL2 portability. ✅
- **Multi-Tenant Isolation**: PostgreSQL RLS is planned for the cloud ingestion layer. ✅

## Project Structure

### Documentation (this feature)

```text
specs/001-foundation-edge-mvp/
├── plan.md              # This file
├── research.md          # Phase 0: Biometric Model Selection
├── data-model.md        # Phase 1: SQLite schema
├── quickstart.md        # Phase 1: Environment setup
├── contracts/           # Phase 1: Sync API Schema
└── tasks.md             # Phase 2: Implementation tasks
```

### Source Code (repository root)

```text
edge/
├── src/
│   ├── hal/             # Hardware Abstraction Layer
│   ├── vision/          # OpenCV & MediaPipe logic
│   ├── biometrics/      # Embedding extraction & HNSW
│   ├── storage/         # SQLite/SQLCipher persistence
│   └── sync/            # MQTT & HTTPS Batcher
└── tests/

cloud/
├── src/
│   ├── api/             # FastAPI endpoints
│   ├── core/            # RLS & Auth logic
│   └── db/              # Postgres migrations
└── tests/
```

## Phase 0: Outline & Research
- **Research Item 1**: Selecting the optimal lightweight embedding model (e.g., MobileFaceNet or MobileNetV3) for sub-200ms inference on Laptop CPU.
- **Research Item 2**: Validating `hnswlib` performance with 1,000 vectors on edge hardware.

## Phase 1: Design & Contracts
- **Data Model**: Finalize SQLite schema for `AttendanceEvent` and `BiometricTemplate`.
- **Contract**: Define the `POST /api/v1/sync/attendance` JSON schema including integrity headers.

## Phase 2: Verification Plan
- **Automated Tests**:
  - `pytest edge/tests/test_biometrics.py`: Verify matching latency and accuracy.
  - `pytest edge/tests/test_sync.py`: Verify batch chunking logic and NTP drift rejection.
- **Manual Verification**:
  - Enrollment test using laptop webcam: Verify 5-pose guidance and successful vector extraction.
  - Offline test: Record 10 events while disconnected, reconnect, and verify cloud persistence.
