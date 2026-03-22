# Multi-Modal Edge-to-Cloud Attendance SaaS (v3.0)

[![Status](https://img.shields.io/badge/Status-Phase_3_Active-blue.svg)](specs/004-advanced-security-mobile/spec.md)
[![Language](https://img.shields.io/badge/Language-Arabic%20%2F%20English-green.svg)](#localization)

An enterprise-grade, AI-powered attendance ecosystem engineered for the Egyptian market. This system leverages advanced facial and periocular recognition at the edge to ensure high accuracy, security, and resilience.

## 🌟 Key Features

- **Multi-Modal AI Recognition**: High-precision facial and periocular biometric matching using on-device HNSW indexing.
- **Bilingual & RTL Support**: Native Arabic/English UI with full Right-to-Left (RTL) mirroring and localized audio prompts.
- **Edge-to-Cloud Resilience**: Operates autonomously with 30-day offline storage; synchronizes via MQTT and HTTPS when connectivity is available.
- **Security & Privacy**: AES-256 encryption, X.509 certificate-based authentication, and a secure "Maker-Checker" workflow for data integrity.
- **Multi-Tenant SaaS**: Scalable cloud backend with Row-Level Security (RLS) for data isolation.

## 🛠 Tech Stack

- **Edge (Kiosk)**: Python, OpenCV, PyTorch Mobile/TFLite, HNSW, SQLite, MQTT.
- **Backend (Cloud)**: FastAPI (Asynchronous Python), PostgreSQL (RLS), AWS IoT Core.
- **Frontend (Web)**: Next.js, TypeScript, Tailwind CSS, `next-intl` (i18n).
- **Mobile**: Flutter/Dart for the Manager Application.

## 🗺 Implementation Roadmap

1. **Phase 1: Foundation & Edge Development (MVP)** - Core kiosk functionality and basic cloud ingestion. **COMPLETE**
2. **Phase 2: Bilingual UI/UX & Manager Dashboard** - Full RTL support and administrative control plane. **COMPLETE**
3. **Phase 3: Advanced Security & Mobile** - Remote wipe, mobile manager app, periocular fallback, encrypted backups. **IN PROGRESS**
4. **Phase 4: Production & Monitoring** - CI/CD, centralized logging, and continuous feedback.

## 🚀 Getting Started

The project has completed **Phase 1** (Foundation) and **Phase 2** (Bilingual UI & Governance) and is now implementing **Phase 3** (Advanced Security & Mobile).

### Development Environment (Laptop/WSL2)
Refer to the [Phase 1 Quickstart](specs/001-foundation-edge-mvp/quickstart.md) to set up the Python environment, simulated camera HAL, and encrypted SQLite edge persistence.

### Prerequisites
- Python 3.9+
- Node.js 18+
- Flutter SDK (for mobile)

### Documentation
- [Phase 1 Spec](specs/001-foundation-edge-mvp/spec.md) &middot; [Quickstart](specs/001-foundation-edge-mvp/quickstart.md)
- [Phase 2 Spec](specs/003-phase2-ui-governance/spec.md) &middot; [Quickstart](specs/003-phase2-ui-governance/quickstart.md)
- [Phase 3 Spec](specs/004-advanced-security-mobile/spec.md) &middot; [Quickstart](specs/004-advanced-security-mobile/quickstart.md) &middot; [Tasks](specs/004-advanced-security-mobile/tasks.md)
- [Comprehensive PRD & Roadmap](comprehensive_prd_and_roadmap.md)
- [Enhanced PRD v3.0](enhanced_prd_v3.0.md)
- [Implementation Roadmap](implementation_roadmap.md)

## ✅ Completed Work

### Phase 1 — Foundation & Edge MVP
- Cloud ingestion API (`/api/v1/*`) with asyncpg + PostgreSQL RLS
- Edge kiosk: OpenCV camera HAL, SQLite/SQLCipher encrypted persistence
- HNSW biometric vector index, audio feedback engine
- MQTT sync pipeline (edge ↔ cloud)

### Phase 2 — Bilingual UI & Governance
- Next.js dashboard with Arabic/English RTL/LTR switching via `next-intl`
- Maker-Checker approval workflow with JWT-based auth and tenant isolation
- Audit logging (decorator + asyncpg persistence)
- IP allow-listing middleware, DiffViewer for approval review
- Settings page with real API integration (GET/PUT IP allowlist)
- 5 Alembic migrations for governance + settings tables

### Phase 3 — Advanced Security & Mobile (29 tasks, IN PROGRESS)
- **Remote Biometric Wipe**: Ed25519 signed commands (cloud sign → edge verify → secure DB wipe + VACUUM)
- **Mobile Manager App**: Flutter skeleton, REST client, alerts feed, manual override with mandatory reason
- **Mobile API**: Device registration (`POST /register`), alerts (`GET /alerts`), override (`POST /override`)
- **Periocular Recognition**: Eye-region ROI extraction via FaceMesh landmarks 133/362 for masked-face fallback
- **Encrypted Backups**: AES-256-GCM via pg_dump + HMAC integrity verification
- **Security Hardening**: `PRAGMA secure_delete = ON` on edge SQLite

## 📄 License
Internal / Proprietary
