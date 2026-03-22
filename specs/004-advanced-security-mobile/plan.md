# Implementation Plan: Phase 3 - Advanced Security & Mobile

**Branch**: `004-advanced-security-mobile` | **Date**: 2026-03-22 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/004-advanced-security-mobile/spec.md`

## Summary
Implement high-security administrative controls and a mobile management suite. Key technical pillars include cryptographically signed remote wipes (Ed25519), periocular recognition fallback using MediaPipe ROI tracking, AES-256 encrypted database backups, and a Flutter-based mobile manager application for real-time unverified event overrides.

## Technical Context

**Language/Version**: Python 3.11 (Edge/Cloud), Dart/Flutter 3.x (Mobile)
**Primary Dependencies**: `FastAPI`, `SQLAlchemy`, `sqlcipher3`, `hnswlib`, `mediapipe`, `pynacl` (Ed25519), `argon2-cffi`, `firebase_messaging` (FCM)
**Storage**: PostgreSQL (Cloud), SQLite/SQLCipher (Edge), Cloud Object Storage (Backups)
**Testing**: `pytest` (Backend/Edge), `flutter test` (Mobile)
**Target Platform**: Linux (Edge/Cloud), Android/iOS (Mobile)
**Project Type**: Multi-tier (Web Service, Mobile App, Edge Service)
**Performance Goals**: <200ms recognition latency (including periocular fallback), <3s notification delivery.
**Constraints**: Zero-trust remote commands (must be signed), AES-256 encryption at rest (Edge/Backups).
**Scale/Scope**: Support for 100+ concurrent kiosks and thousands of mobile notifications/day.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

1. **Principle I (Privacy)**: Biometric vectors must be encrypted. -> **PASS**: Using SQLCipher on Edge and AES-GCM for Backups.
2. **Principle II (Edge-First)**: Matching must be local with <200ms latency. -> **PASS**: HNSW and MediaPipe Periocular ROI both execute on-device.
3. **Principle III (Inclusive UX)**: Periocular fallback for masks/niqabs. -> **PASS**: Core feature of Phase 3.
4. **Principle V (Governance)**: Maker-Checker for manual overrides. -> **PASS**: Mobile app implementer mandatory reason requirement.

## Project Structure

### Documentation (this feature)

```text
specs/004-advanced-security-mobile/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── mobile_api.md
└── checklists/
    └── requirements.md
```

### Source Code

```text
cloud/
├── src/
│   ├── services/backup.py      # New backup engine
│   ├── api/mobile_mgmt.py      # New mobile endpoints
│   └── utils/signing.py        # Ed25519 signature logic
└── tests/

edge/
├── src/
│   ├── biometrics/wipe.py      # Wipe execution logic
│   └── vision/periocular.py    # ROI-based ocular recognition
└── tests/

mobile/                         # [NEW] Flutter Project
├── lib/
│   ├── models/
│   ├── providers/              # State management (Riverpod)
│   ├── screens/                # Alerts feed, Override screen
│   └── services/               # API & FCM integration
└── test/
```

**Structure Decision**: Added a new top-level `mobile/` directory for the Flutter app and extended `cloud/` and `edge/` with the new security modules.

## Verification Plan

### Automated Tests
- **Cloud (Pytest)**: `pytest cloud/tests/integration/test_mobile_api.py` (Mocking mobile registration and override).
- **Edge (Pytest)**: `pytest edge/tests/unit/test_periocular.py` (Verifying ROI cropping logic).
- **Security (Pytest)**: `pytest cloud/tests/unit/test_signing.py` (Verify Ed25519 payload generation and verification).

### Manual Verification
1. **End-to-End Wipe**: Issue a Wipe command from the admin dashboard (mocked) and verify the `.db` and `.hnsw` files on the edge are deleted.
2. **Push Notification Loop**: Trigger a low-confidence match on a dev-mode kiosk and verify a notification appears on the Flutter Emulator.
3. **Mask Recognition**: Perform a match wearing a medical mask and verify the logs show "Periocular Fallback" trigger. Verify SC-004 backup decryption performance.
