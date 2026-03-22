# Phase 0 Research: Phase 3 Advanced Security & Mobile

## Decision 1: Cryptographically Signed Remote Wipe
- **Problem**: How to ensure a "Wipe" command is authentic and once-only?
- **Decision**: Use **Ed25519** signatures (via `PyNaCl`).
- **Rationale**: Extremely fast verification on edge hardware, small signature size (64 bytes), and highly secure.
- **Implementation**: 
  - Cloud signs a payload containing `kiosk_id`, `timestamp`, and `nonce`.
  - Edge verifies before executing `EncryptedDB.secure_wipe()` and `VectorIndex.clear()`.
- **Alternatives**: RSA-4096 (Too slow for edge), HMAC (Key management per-device is harder than public key distribution).

## Decision 2: Periocular Recognition Fallback
- **Problem**: Recognition failing due to masks/niqabs.
- **Decision**: Use **MediaPipe FaceMesh** eye landmarks to define a static ROI (Region of Interest) for the ocular region.
- **Rationale**: FaceMesh already running for pose; eye coordinates (133, 362) are stable even with masks.
- **Implementation**: 
  - If lower face landmarks (mouth/chin) detection confidence < 0.3, crop the frame to the ocular ROI.
  - Pass crop to a specialized embedding model or the primary model if trained on masked faces.
- **Alternatives**: Infrared (Hardware dependent), Thermal (Expensive).

## Decision 3: High-Security Automated Backups
- **Problem**: Secure off-site disaster recovery.
- **Decision**: **AES-256-GCM** encryption via `OpenSSL` on `pg_dump` streams.
- **Rationale**: Native database tools are most reliable; GCM provides authenticated encryption.
- **Implementation**: 
  - Scheduled task (Celery/Cron) runs `pg_dump`.
  - Piped to `openssl enc -aes-256-gcm` with a rotating master key.
  - Uploaded to Cloud Object Storage (S3/Blob).
- **Alternatives**: Database-level encryption (TDE) (often requires enterprise versions).

## Decision 4: Mobile Manager App Architecture
- **Problem**: Native-feel UI with cross-platform efficiency.
- **Decision**: **Flutter** + **Firebase Cloud Messaging (FCM)**.
- **Rationale**: Fast development, shared logic for Android/iOS, reliable push delivery.
- **Implementation**: 
  - Provider/Riverpod for state management.
  - `firebase_messaging` for background alerts.
  - `dio` for secure API calls with Bearer tokens.
- **Alternatives**: React Native (Slightly slower performance for image-heavy grids).
