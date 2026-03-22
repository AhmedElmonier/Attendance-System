# Multi-Modal Edge-to-Cloud Attendance SaaS (v3.0)

[![Status](https://img.shields.io/badge/Status-Phase_2_Active-green.svg)](comprehensive_prd_and_roadmap.md)
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

1. **Phase 1: Foundation & Edge Development (MVP)** - Core kiosk functionality and basic cloud ingestion.
2. **Phase 2: Bilingual UI/UX & Manager Dashboard** - Full RTL support and administrative control plane (Currently Active).
3. **Phase 3: Advanced Features & Scalability** - Mobile app, vector purge broadcast, and high-availability deployment.
4. **Phase 4: Production & Monitoring** - CI/CD, centralized logging, and continuous feedback.

## 🚀 Getting Started

Currently, the project has completed **Phase 1: Foundation & Edge MVP** and is entering **Phase 2**.

### Development Environment (Laptop/WSL2)
Refer to the [Phase 1 Quickstart](specs/001-foundation-edge-mvp/quickstart.md) to set up the Python environment, simulated camera HAL, and encrypted SQLite edge persistence.

### Prerequisites
- Python 3.9+
- Node.js 18+
- Flutter SDK (for mobile)

### Documentation
- [Comprehensive PRD & Roadmap](comprehensive_prd_and_roadmap.md)
- [Enhanced PRD v3.0](enhanced_prd_v3.0.md)
- [Implementation Roadmap](implementation_roadmap.md)

## 📄 License
Internal / Proprietary
