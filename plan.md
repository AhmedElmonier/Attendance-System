# Implementation Plan: Multi-Modal Edge-to-Cloud Attendance SaaS (v3.0)

## 0. Project Vision
To build a resilient, high-accuracy attendance system tailored for the Egyptian market, featuring dual-language (AR/EN) support, RTL UI mirroring, and edge-side AI for offline robustness.

---

## 1. Technical Architecture Summary

### 1.1 Edge Kiosk (The "Node") - Development Environment
- **Hardware**: Local Machine / Laptop (Built-in Webcam).
- **OS Option**: Windows (Native) or **WSL2 (Windows Subsystem for Linux)**. WSL2 is recommended for mirroring the target Linux environment on a Raspberry Pi.
- **HAL (Hardware Abstraction Layer)**: Design code to abstract camera and I/O access. Note: WSL2 requires `usbipd-win` for USB webcam passthrough, or we can develop the vision core on Windows and the logic core on WSL2.
- **Language**: Python 3.9+.
- **Vision**: OpenCV for capture, MediaPipe for Euler angle detection.
- **Biometrics**: PyTorch / TensorFlow Lite (MobileNetV3 backbone), HNSW (Hierarchical Navigable Small World) for <200ms local vector matching.
- **Persistence**: Encrypted SQLite for logs and metrics; 30-day offline blackout buffer.
- **Sync**: MQTT (AWS IoT Core) for telemetry; HTTPS (FastAPI) for batched sync.

### 1.2 Cloud Backend (The "Brain")
- **Framework**: FastAPI (Asynchronous Python).
- **Database**: PostgreSQL with Row-Level Security (RLS) for multi-tenancy.
- **Security**: X.509 Device Certificates, JWT for dashboard auth.
- **Notifications**: WhatsApp (Twilio/WABA), Email (SES).

### 1.3 Management Dashboard (The "Control Plane")
- **Framework**: Next.js (React), TypeScript.
- **Styling**: Tailwind CSS (Logical Properties for RTL).
- **i18n**: `next-intl` for seamless AR/EN switching.
- **Analytics**: Chart.js with RTL support.

---

## 2. Phase 1: Foundation & Edge MVP (Weeks 1-8)

### 2.1 Edge Core Infrastructure
- [ ] **Environment Setup**: Python virtual environment on Dev Machine with built-in webcam support.
- [ ] **HAL Implementation**: Stub out I/O features (like GPIO for locks) that won't be present on the laptop.
- [ ] **Local DB Schema**: SQLite with encryption-at-rest.
- [ ] **Camera Module**: Implement multi-angle capture using standard laptop camera.

### 2.2 Biometric Pipeline
- [ ] **Detection**: Integration of Face Mesh for Euler angle verification.
- [ ] **Extraction**: Integration of Face embedding model (MobileNetV3 based).
- [ ] **Indexing**: Implementation of HNSW for sub-second similarity search.

### 2.3 Foundational Backend
- [ ] **API Core**: FastAPI base with PostgreSQL integration.
- [ ] **RLS Setup**: Implement basic multi-tenant isolation at the DB level.
- [ ] **Device Provisioning**: AWS IoT Core setup and basic MQTT heartbeat.

---

## 3. Phase 2: Bilingual UI/UX & Governance (Weeks 9-16)

### 3.1 Web Dashboard (AR/EN)
- [ ] **i18n Implementation**: Set up `next-intl` and logical properties for RTL flow.
- [ ] **Role-Based Access (RBAC)**: Define Manager and Admin roles with JWT auth.
- [ ] **Management Modules**: Employee profiles, kiosk status monitors, and real-time attendance feeds.

### 3.2 Maker-Checker Workflow
- [ ] **Audit Trail**: Implement "Pending Approval" state for all sensitive edits.
- [ ] **Approvals Inbox**: checker interface with "Original vs Proposed" diff view and localized reason translation.

### 3.3 Kiosk UI Polish
- [ ] **Flutter UI**: Complete RTL mirroring and interactive enrollment animation.
- [ ] **Audio Engine**: Localized voice prompts for "Success", "Retry", etc.

---

## 4. Phase 3: Advanced Security & Mobile (Weeks 17-22)

### 4.1 Biometric Lifecycle
- [ ] **Vector Purge**: Implement the cryptographically signed "Wipe Vector" broadcast via MQTT.
- [ ] **Periocular Fallback**: Enhanced identification for obscured faces (masks/niqabs).

### 4.2 Security Hardening
- [ ] **Backup Engine**: Implementation of AES-256 + Argon2id key derivation for "No-Trap" backups.
- [ ] **Penetration Testing**: Initial internal security audit of the sync protocol.

### 4.3 Mobile Manager App
- [ ] **Flutter Mobile**: Cross-platform app for real-time alerts and "Unverified" event overrides.
- [ ] **Push Notifications**: FCM/APNS integration for critial alerts.

---

## 5. Phase 4: Production Scalability (Weeks 23-28)

### 5.1 Cloud Orchestration
- [ ] **Containerization**: Dockerize all services.
- [ ] **Orchestration**: Deploy to K8s (EKS/GKE) with Horizontal Pod Autoscaling (HPA).

### 5.2 Observability
- [ ] **Centralized Logging**: ELK or CloudWatch Logs for distributed traces.
- [ ] **Monitoring**: Prometheus/Grafana for inference latency and API error rates.

### 5.3 CI/CD & Deployment
- [ ] **Pipelines**: GitHub Actions for automated testing and staging/prod deployments.

---

## 6. Success Metrics (KPIs)
- **Latency**: $< 200\text{ms}$ enrollment/matching on-edge.
- **Accuracy**: $FAR < 0.001\%$.
- **Resilience**: 100% data recovery after simulated 7-day offline period.
- **UX**: $\le 2$ clicks for most common administrative actions.
