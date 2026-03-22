# PRD: Multi-Modal Edge-to-Cloud Attendance SaaS (v3.0)

**Author:** Manus AI (Senior SaaS Developer Persona)
**Date:** March 22, 2026
**Version:** 3.0

## 0. Executive Summary

This document outlines the enhanced Product Requirements for a Multi-Modal Edge-to-Cloud Attendance SaaS, specifically engineered for the Egyptian market. The system leverages advanced AI for facial and periocular recognition at the edge, ensuring high accuracy and resilience even in offline scenarios. A core focus is robust bilingual (Arabic/English) support, including Right-to-Left (RTL) UI mirroring and localized audio prompts, to deliver a seamless and culturally appropriate user experience. The architecture emphasizes scalability, security, and data integrity, employing a modern tech stack and a comprehensive governance framework. This PRD serves as the foundational technical specification for engineering, design, and QA teams, guiding the development of a reliable, high-performance, and user-centric attendance ecosystem.

## 1. Project Vision & Strategic Objectives

### 1.1 Vision Statement

To establish the leading enterprise-grade attendance ecosystem in the Egyptian market, empowering organizations with an intelligent, highly accurate, and resilient multi-modal solution that seamlessly integrates bilingual (Arabic/English) capabilities across all touchpoints, thereby optimizing workforce management and ensuring compliance.

### 1.2 Core Success KPIs & Technical Rationale

Key Performance Indicators (KPIs) are defined with specific technical objectives and their underlying rationale to ensure alignment across development and operations. These metrics are critical for validating system performance, user experience, and security posture.

| Category | Metric | Target Objective | Technical Rationale & Impact |
| :--- | :--- | :--- | :--- |
| **User Experience** | Inference Latency (Edge) | $< 200\text{ms}$ | Critical for real-time feedback at the kiosk, minimizing user wait times and perceived system responsiveness. Achieved via optimized on-device AI models (e.g., quantized PyTorch models) and efficient HNSW indexing for vector similarity search. |
| **User Experience** | Language Switch (Dashboard/Kiosk) | Instant (No page reload) | Essential for a fluid bilingual user experience, particularly in shared environments or for users frequently switching languages. Implemented via client-side rendering (Next.js/Flutter) and dynamic content loading with `next-intl` for web and `i18n-ready` for mobile. |
| **AI Accuracy** | $FAR$ (False Acceptance Rate) | $< 0.001\%$ | High-security threshold to prevent unauthorized access. This requires a robust facial recognition model with a high decision boundary threshold ($C \ge 0.85$) and stringent enrollment quality checks. |
| **AI Accuracy** | $FRR$ (False Rejection Rate) - Face | $< 1\%$ | Acceptable rejection rate under standard conditions (frontal pose, adequate lighting). Optimized via comprehensive training datasets and robust feature extraction. |
| **AI Accuracy** | $FRR$ (False Rejection Rate) - Periocular | $< 5\%$ | Specialized metric for challenging scenarios (e.g., Niqab/Mask wearers). Achieved through a dedicated periocular recognition module, requiring specialized training data and potentially a lower decision boundary for this specific modality. |
| **System Resilience** | Offline Data Storage | 30 days (min) | Ensures business continuity during network outages. Requires robust SQLite implementation at the edge with efficient data compression and a prioritized sync mechanism. |
| **Data Integrity** | NTP Sync Drift Rejection | $>\pm 5\text{ mins}$ | Prevents time manipulation and ensures accurate attendance records. Enforced by cloud-side validation of edge device timestamps against NTP-synchronized server time. |

## 2. Bilingual UI/UX & Localization (i18n)

### 2.1 The RTL (Right-to-Left) Mandate: Technical Implementation

Full support for Right-to-Left (RTL) languages, specifically Arabic, is a non-negotiable requirement, extending beyond simple text translation to comprehensive UI mirroring and layout adaptation. This mandates a `mobile-first` and `logical-property-first` design approach.

*   **Directional Mirroring (Web - Next.js/TailwindCSS)**:
    *   The primary mechanism for RTL activation will be a top-level `<html dir="rtl" lang="ar">` attribute on the `<html>` tag, dynamically set based on the detected locale (`ar`).
    *   **CSS Logical Properties**: Strict adherence to Tailwind CSS Logical Properties (e.g., `ps-4` for `padding-inline-start`, `me-auto` for `margin-inline-end`) is mandatory. This ensures layout elements (padding, margin, borders, text alignment) automatically adapt to the writing direction without requiring separate RTL-specific stylesheets.
    *   **Iconography & Visual Assets**: Icons with inherent directionality (e.g., arrows, navigation icons) must be mirrored horizontally when `dir="rtl"` is active. This requires a component-level logic or a CSS transformation (`transform: scaleX(-1);`) applied conditionally. All SVG assets and images used in the UI must be designed to be direction-agnostic or provide RTL-specific variants.
    *   **Text Alignment**: Default text alignment for Arabic content will be `text-right` for block-level elements, while English content will default to `text-left`. This will be managed via CSS classes applied conditionally based on the active language.
    *   **Data Visualization (Chart.js)**: All data visualizations (e.g., bar charts, line graphs) must adapt their axis labels, legends, and data flow direction to RTL. This requires configuring Chart.js instances with appropriate RTL settings (e.g., `options.indexAxis = 'y'` for horizontal bar charts, `options.rtl = true`).

*   **Directional Mirroring (Mobile - Flutter)**:
    *   Flutter's `Directionality` widget and `Locale` settings will be leveraged to manage RTL. The `MaterialApp` widget will be configured with `locale` and `supportedLocales` to enable automatic widget mirroring.
    *   Widgets like `Row`, `Column`, `ListView`, and `Text` will inherently adapt to the `TextDirection` (`rtl` or `ltr`) provided by the `Directionality` widget. Custom widgets must explicitly respect `Directionality.of(context).textDirection`.
    *   **Iconography**: Similar to web, directional icons must be handled programmatically, potentially using `Transform.flip` or providing RTL-specific icon assets.

### 2.2 Edge Kiosk Localization

The Edge Kiosk requires a highly intuitive and robust bilingual interface, minimizing reliance on complex text and maximizing universal visual and auditory cues.

*   **Bilingual Audio Prompts**: Pre-recorded audio prompts in both Arabic and English will be stored locally on the edge device. The system will dynamically select and play the appropriate audio file based on the Kiosk's configured language or user selection. Examples:
    *   "Identity Confirmed" / "تم تأكيد الهوية"
    *   "Please look at the camera" / "الرجاء النظر إلى الكاميرا"
    *   **Implementation**: Audio files (e.g., MP3, WAV) will be managed via a simple key-value store, with keys mapped to specific events or messages. A dedicated audio playback module will handle buffering and playback.

*   **Visual Cues & Universal Iconography**: Heavy reliance on universally understood icons and color-coding to convey status and instructions. This reduces cognitive load and improves usability across language barriers.
    *   **Green Checkmark**: Success, Identity Confirmed, Action Completed.
    *   **Red X**: Failure, Identity Not Recognized, Error.
    *   **Yellow Exclamation**: Warning, Unverified, Action Required.
    *   **Implementation**: A standardized icon library (e.g., Font Awesome, Material Icons) will be used, ensuring consistent visual language. Custom icons will be designed with internationalization in mind.

*   **Dual-Language Enrollment Wizard**: A step-by-step guided enrollment process that supports both Arabic and English simultaneously or allows for easy switching. This is crucial for accurate data capture and user understanding.
    *   **Guided Head-Pose Instructions**: Visual aids (e.g., animated GIFs, real-time 3D model overlays, clear diagrams) will demonstrate the required head poses (Center, $\pm 30^\circ$ Yaw, $\pm 15^\circ$ Pitch). Textual instructions will be presented bilingually or switchable.
    *   **Real-time Feedback**: The Kiosk UI will provide immediate visual and auditory feedback on head-pose compliance (e.g., "Move head left", "Tilt head up").
    *   **Confirmation**: Each step will require explicit confirmation from the user before proceeding, ensuring comprehension.

## 3. The AI Pipeline & Enrollment UX

### 3.1 Enrollment "Genesis" Flow: Technical Deep Dive

The enrollment process is critical for the accuracy and security of the entire system, focusing on high-quality biometric data capture and efficient indexing.

*   **Guided Multi-Angle High-Resolution Capture**: The edge device (Kiosk) will utilize its camera to capture a sequence of high-resolution images based on precise Euler angles.
    *   **Euler Angle Detection**: An on-device lightweight AI model (e.g., MediaPipe Face Mesh or a custom-trained model) will continuously estimate the user's head pose (Yaw, Pitch, Roll). The system will trigger image capture only when the estimated angles fall within predefined thresholds for each of the 5 required angles (Center, $\pm 30^\circ$ Yaw, $\pm 15^\circ$ Pitch).
    *   **Image Quality Assessment**: Each captured image will undergo immediate on-device quality checks for blur, illumination, and occlusion before being accepted. Poor quality images will trigger re-capture prompts.
    *   **User Feedback**: Real-time visual (e.g., a 3D head model guiding movement) and auditory prompts will guide the user through the capture process.

*   **Biometric Feature Extraction**: For each accepted image, a pre-trained deep learning model (e.g., a MobileNetV3-based facial recognition backbone) will extract a high-dimensional biometric vector (e.g., 512-dimension embedding).
    *   **On-Device Model**: The model will be optimized for edge deployment (e.g., TensorFlow Lite, PyTorch Mobile) to ensure low latency and minimal resource consumption.

*   **HNSW (Hierarchical Navigable Small World) Indexing**: The extracted biometric vectors will be indexed locally on the edge device using an HNSW graph for rapid similarity search.
    *   **Rationale**: HNSW provides $O(\log N)$ search complexity, making it ideal for large-scale, low-latency biometric matching on edge devices. It balances search speed with memory footprint effectively [1].
    *   **Implementation**: A SQLite database will store metadata, and the HNSW index will be built and maintained in-memory or persisted to disk for fast loading. Updates to the index (new enrollments, deletions) will be handled incrementally.

*   **Mesh Sync: Encrypted Vector Blobs via Blind Cloud Relay**: Biometric vectors (encrypted) and associated metadata will be securely synchronized to the cloud and across the local mesh of edge devices.
    *   **Encrypted Vector Blobs**: The 512-dimension biometric vectors will be encrypted using AES-256 GCM with a unique, ephemeral key derived per enrollment session. This key will be part of a larger encrypted payload, ensuring that raw biometric data is never transmitted or stored in plaintext.
    *   **Blind Cloud Relay**: A secure, intermediary cloud service (e.g., AWS IoT Core with custom Lambda functions) will act as a relay. This service will *not* have access to the decryption keys for the biometric blobs. Its role is solely to route encrypted payloads from edge devices to the central backend and facilitate mesh synchronization.
    *   **60-second SLA**: The system guarantees that an enrolled biometric vector will be available for recognition across the mesh and in the cloud within 60 seconds of successful enrollment. This requires efficient message queuing (MQTT) and robust synchronization protocols.

### 3.2 Decision Boundary & Fallback Mechanisms

Automated decision-making based on biometric confidence scores, coupled with intelligent fallback mechanisms, ensures both security and usability. The system defines three distinct zones for biometric matching, each with specific actions and user experiences:

| Zone | Confidence Score (C) | Action | User Experience | Manager/Admin Action |
| :--- | :--- | :--- | :--- | :--- |
| **Green Zone** | $C \ge 0.85$ | Auto-Commit | Instant "Identity Confirmed" audio prompt and green visual cue. | No action required. |
| **Gray Zone** | $0.75 \le C < 0.85$ | Log-and-Continue with "Unverified" Flag | "Identity Partially Verified, Manager Review Required" audio prompt and yellow visual cue. User is informed that entry is recorded but requires review. | Managers receive real-time alerts (Dashboard, WhatsApp, Email) with event details, captured image, and confidence score. Manual approval or rejection updates the system. |
| **Red Zone** | $C < 0.75$ | Instant Rejection; Trigger Hard Fallback | "Identity Not Recognized, Please use alternative method" audio prompt and red visual cue. | Alerts generated for potential security incidents. System prompts for alternative identification. |

For the **Red Zone**, the system automatically prompts the user for an alternative identification method. This includes presenting an RFID card to the Kiosk or a supervisor/manager performing a manual override via a secure interface on the Kiosk or a separate mobile application. Manual overrides require manager credentials and a documented reason.

## 4. Technical Architecture & Resilience

### 4.1 Connectivity & Data Synchronization

Robust data handling, especially in environments with intermittent connectivity, is paramount for an edge-to-cloud system. The architecture supports both real-time telemetry and batched data synchronization.

**Telemetry (MQTT via AWS IoT Core)**: This channel is used for real-time, lightweight communication, including device health, status updates, and Over-The-Air (OTA) command triggers. MQTT 3.1.1 over TLS 1.2 ensures secure, low-bandwidth communication. AWS IoT Core provides a managed MQTT broker, device shadows, and a rule engine for scalable and secure device connectivity. Edge devices publish a heartbeat message every 60 seconds, containing device ID, battery status, and network connectivity status. Cloud-initiated commands, such as firmware updates or configuration changes, are pushed via MQTT topics.

**Data Sync (HTTPS POST with Exponential Backoff)**: Batch synchronization of attendance logs, enrollment data, and other non-real-time data occurs via HTTPS POST requests to a dedicated FastAPI API endpoint. Data is batched on the edge device to minimize network overhead, with configurable batch size and frequency. In case of network failures, an exponential backoff strategy is implemented for retrying failed POST requests, preventing network congestion. Each batch includes a cryptographic hash (e.g., SHA-256) to ensure data integrity during transmission.

**Offline Blackout Resilience**: The edge device is designed for autonomous operation during extended periods of cloud disconnection. All critical attendance events and biometric data are stored locally in an encrypted SQLite database, guaranteeing a minimum of 30 days of operational data storage through efficient data compression and management. When local storage reaches 90% capacity (e.g., 8GB out of 9GB total), the system prioritizes new Clock-In/Clock-Out events over telemetry data, potentially purging older telemetry to preserve critical records. An alert (MQTT telemetry, local UI notification) is triggered at 80% capacity, notifying administrators of impending storage issues. A configurable retention policy ensures older, successfully synced data is purged first.

### 4.2 Temporal Integrity

Accurate timekeeping is fundamental for attendance systems, requiring robust synchronization and drift detection.

**NTP Guard**: Edge devices perform mandatory NTP synchronization every 60 minutes, utilizing `ntpd` or `chronyd` on Linux-based devices configured with reliable NTP servers. If NTP sync fails, the device logs the event and attempts to resynchronize at shorter intervals.

**Drift Rejection (Cloud-side)**: The cloud backend rejects any attendance or enrollment sync requests where the edge device's reported timestamp deviates by more than $\pm 5\text{ minutes}$ from the server's NTP-synchronized time. This is enforced by comparing the `device_timestamp` header with the `server_timestamp` upon data receipt. Rejected syncs trigger alerts to system administrators, indicating potential timekeeping issues or malicious attempts, which can be resolved remotely via OTA commands.

## 5. Governance & Security

### 5.1 Bilingual Maker-Checker Workflow

This workflow ensures data accuracy and accountability through a two-person control process, fully localized for the Egyptian market.

**Maker (Manager Role)**: A manager initiates an edit to an attendance record or employee profile. The system automatically records the original data, proposed changes, `maker_id`, and timestamp, placing the record in a "Pending Approval" state until approved by a Checker.

**Checker (Admin Role)**: Administrators receive real-time alerts (Dashboard, WhatsApp, Email) in their `preferred_language` for pending approvals. A dedicated "Approvals Inbox" in the admin dashboard displays pending changes, showing original vs. proposed values, the reason for change (provided by the Maker), and a 1-click **[Translate]** toggle for the reason. Checkers can `Approve` or `Reject` changes, with both actions logged including `checker_id`, timestamp, and reason.

### 5.2 Data Deletion & Failsafes

Comprehensive data deletion policies with failsafes ensure compliance and prevent accidental data loss.

**Individual Biometric Purge ("Wipe Vector" Broadcast)**: Deletion of an employee's biometric data triggers a cryptographically signed "Wipe Vector" command via MQTT to all subscribed edge devices and the cloud backend. Each device securely deletes the corresponding biometric vector from its local HNSW index and SQLite database. The central backend purges the vector from its PostgreSQL database and associated backups. The system verifies successful purge across all registered devices.

**Tenant Deletion (Soft-Delete with Challenge)**: Deletion of an entire organization's data is a critical operation with multiple safeguards. A text-match challenge (typing the full company name) prevents accidental deletion. Upon confirmation, data is "soft-deleted" for a 30-day "Tombstone Period," during which it can be recovered by an authorized super-administrator. After 30 days, data is permanently purged from all primary databases and backups, ensuring compliance.

**No-Trap Backups**: A robust backup strategy prevents unauthorized access to backup data. All backup data (PostgreSQL dumps, S3 object storage) is encrypted at rest using AES-256. Encryption keys are derived using Argon2id from a combination of the Admin Password and the Tenant UUID, ensuring unique, brute-force-resistant keys that are never stored directly. Recovery requires both the Admin Password and the Tenant UUID, preventing single points of compromise. Key management is handled via a secure, separate system (e.g., AWS KMS) or strict procedural controls.

## 6. Tech Stack Summary & Rationale

This section provides a high-level overview of the chosen technology stack, with brief justifications for key selections, emphasizing scalability, performance, and maintainability.

| Component | Technologies | Rationale |
| :--- | :--- | :--- |
| **Edge (Kiosk)** | Python (3.9+), OpenCV, PyTorch Mobile/TensorFlow Lite, HNSW, SQLite, Paho MQTT client, `requests` | Python offers a rich ecosystem for AI/ML and rapid development. SQLite provides a reliable embedded database. Optimized AI frameworks ensure edge performance. |
| **Backend (Cloud)** | FastAPI (Python), Babel (i18n), PostgreSQL (with Row-Level Security - RLS) | FastAPI provides extremely high performance and asynchronous capabilities, ideal for high-throughput API requests. PostgreSQL offers advanced features like RLS, crucial for multi-tenancy and data isolation. Babel simplifies i18n management. |
| **Frontend (Web Dashboard)** | Next.js (React), TypeScript, Tailwind CSS, `next-intl` | Next.js provides SSR/SSG for performance and SEO, with a robust component-based architecture. TypeScript enhances code quality. Tailwind CSS enables rapid UI development. `next-intl` offers comprehensive i18n, including dynamic language switching. |
| **Mobile (Manager App)** | Flutter, `i18n-ready` (or similar), TFLite | Flutter enables cross-platform development from a single codebase, accelerating development and ensuring consistent UI/UX. Its performance is near-native. TFLite allows for future on-device AI capabilities. |

## 7. Future Considerations & Scalability

To ensure long-term viability and adaptability, the system is designed with future enhancements and scalability in mind. Horizontal scaling of the cloud backend (FastAPI, PostgreSQL) will be achieved through containerization (Docker/Kubernetes) and managed database services (e.g., AWS RDS, Aurora). Future iterations will include advanced remote management capabilities for edge devices, such as batch configuration updates, predictive maintenance, and enhanced monitoring. Exploration of additional biometric modalities (e.g., fingerprint, iris scan) will enhance security and cater to diverse user needs. Finally, integration with business intelligence tools will provide deeper insights into attendance patterns, workforce productivity, and system performance.

## 8. Glossary

*   **AES-256 GCM**: Advanced Encryption Standard with 256-bit keys in Galois/Counter Mode, a highly secure authenticated encryption algorithm.
*   **Argon2id**: A memory-hard key derivation function designed to resist brute-force attacks and GPU-based cracking.
*   **C**: Confidence Score, a metric indicating the likelihood of a correct biometric match.
*   **Euler Angles**: A set of three angles (Yaw, Pitch, Roll) used to describe the orientation of a rigid body (e.g., a human head) in 3D space.
*   **FAR (False Acceptance Rate)**: The rate at which a biometric system incorrectly matches an unauthorized user to a valid enrolled template.
*   **FastAPI**: A modern, fast (high-performance) web framework for building APIs with Python 3.7+ based on standard Python type hints.
*   **FRR (False Rejection Rate)**: The rate at which a biometric system fails to match an authorized user to their valid enrolled template.
*   **HNSW (Hierarchical Navigable Small World)**: An efficient algorithm for approximate nearest neighbor search in high-dimensional spaces.
*   **i18n**: Abbreviation for Internationalization, the process of designing a software application so that it can be adapted to various languages and regions without engineering changes.
*   **KPI**: Key Performance Indicator, a measurable value that demonstrates how effectively a company is achieving key business objectives.
*   **LTR**: Left-to-Right, the writing direction for languages like English.
*   **MQTT**: Message Queuing Telemetry Transport, a lightweight messaging protocol for small sensors and mobile devices, optimized for high-latency or unreliable networks.
*   **NTP**: Network Time Protocol, a networking protocol for clock synchronization between computer systems over packet-switched, variable-latency data networks.
*   **OTA**: Over-The-Air, refers to the wireless delivery of new software, firmware, or configuration settings to electronic devices.
*   **Periocular Recognition**: Biometric identification based on the region around the eye, useful when parts of the face are obscured.
*   **PRD**: Product Requirements Document, a document that specifies the requirements of a particular product.
*   **PostgreSQL**: A powerful, open-source object-relational database system with a strong reputation for reliability, feature robustness, and performance.
*   **RLS (Row-Level Security)**: A database feature that restricts which rows a user can see or manipulate in a table, based on their role or other criteria.
*   **RTL**: Right-to-Left, the writing direction for languages like Arabic.
*   **SaaS**: Software as a Service, a software distribution model in which a third-party provider hosts applications and makes them available to customers over the Internet.
*   **SLA**: Service Level Agreement, a commitment between a service provider and a client.
*   **SQLite**: A C-language library that implements a small, fast, self-contained, high-reliability, full-featured, SQL database engine.
*   **Tailwind CSS**: A utility-first CSS framework for rapidly building custom user interfaces.
*   **Telemetry**: The process of recording and transmitting the readings of an instrument.
*   **Tenant UUID**: A universally unique identifier assigned to each tenant (organization) in a multi-tenant SaaS application.
*   **TypeScript**: A strongly typed superset of JavaScript that compiles to plain JavaScript.

## 9. References

[1] Malkov, Y. A., & Yashunin, D. A. (2018). Efficient and robust approximate nearest neighbor search using Hierarchical Navigable Small World graphs. *IEEE Transactions on Pattern Analysis and Machine Intelligence*, *40*(12), 2999-3009. [https://arxiv.org/abs/1603.09320](https://arxiv.org/abs/1603.09320)
