# Phase 3 Quickstart Guide

This guide covers setup for the **Advanced Security & Mobile** features.

## 1. Cloud Backend Setup
Ensure the following environment variables are set in `cloud/.env`:
- `ED25519_PRIVATE_KEY`: hex-encoded private key for signing remote wipes.
- `ED25519_PUBLIC_KEY`: hex-encoded public key for wipe verification on edge.
- `MASTER_BACKUP_KEY`: 32-byte hex string for AES-256-GCM.
- `FCM_SERVER_KEY`: Firebase Cloud Messaging server key.

Generate Ed25519 keys:
```bash
python -c "from nacl.signing import SigningKey; sk = SigningKey.generate(); print('PRIVATE:', sk.encode().hex()); print('PUBLIC:', sk.verify_key.encode().hex())"
```

## 2. Mobile Manager App (Flutter)
Prerequisites: Flutter SDK 3.x installed.

```bash
cd mobile
flutter pub get
# Create a firebase project and add google-services.json (Android) / GoogleService-Info.plist (iOS)
```

## 3. Edge Kiosk (Security)
Prerequisites: `sqlcipher3` and `pynacl` installed.

```bash
cd edge
pip install -r requirements.txt
# Ensure ED25519_PUBLIC_KEY is configured in the local config for wipe verification.
```

## 4. Running Backups
To manually trigger a high-security backup:
```bash
cd cloud
python -m src.services.backup --trigger
```
