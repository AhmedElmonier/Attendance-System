# Feature Specification: Foundation & Edge MVP (Phase 1)

**Feature Branch**: `001-foundation-edge-mvp`  
**Created**: 2026-03-22  
**Status**: Draft  
**Input**: User description: "Foundation & Edge MVP Phase 1 based on plan.md"

## Clarifications

### Session 2026-03-22
- Q: Enrollment Interaction Fallback → A: Immediate Real-time Retry. Show live feedback and stay on the current pose until valid.
- Q: Sync Batch Strategy → A: Chunked Batches. Push in small chunks (e.g., 500 logs) sequentially.
- Q: Multiple Faces in Frame → A: Primary Face Focus. Identify and process only the largest/most centered face.
- Q: Low-Light / Poor Quality Thresholds → A: Retry + Admin Notification. Guide user through better environments and log failures for admin review. Phase 3.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Biometric Enrollment (Priority: P1)
As a new employee, I want to be guided through a multi-angle facial capture process (enrollment) so that my biometric template is securely stored and I can be recognized for attendance.

**Why this priority**: Enrollment is the "genesis" of the system; without it, no attendance can be recorded.
**Independent Test**: Can be tested by running the enrollment wizard and verifying that a new entry appears in the local HNSW index and SQLite database.

**Acceptance Scenarios**:
1. **Given** the kiosk is in enrollment mode, **When** I look at the camera, **Then** the system guides me to move my head to 5 specific angles (Center, Left, Right, Up, Down).
2. **Given** 5 high-quality images are captured, **When** processing is complete, **Then** a 512-dimension vector is extracted and saved to the local HNSW index.

---

### User Story 2 - Offline Attendance Clock-In (Priority: P1)
As an enrolled employee, I want to stand in front of the kiosk and have my attendance recorded instantly, even if the building's internet is currently down.

**Why this priority**: Correcting attendance is the primary value proposition; offline resilience is a non-negotiable principle.
**Independent Test**: Disconnect the network, perform a clock-in, and verify the "Identity Confirmed" prompt and local log entry.

**Acceptance Scenarios**:
1. **Given** I am enrolled, **When** I stand in front of the camera, **Then** I receive a green visual cue and an "Identity Confirmed" audio prompt in under 200ms.
2. **Given** the kiosk is offline, **When** I clock in, **Then** the event is stored in the local encrypted SQLite database for later sync.

---

### User Story 3 - Batch Synchronization (Priority: P2)
As a system administrator, I want the kiosk to automatically upload all accumulated attendance logs once the internet connection is restored.

**Why this priority**: Ensures the cloud dashboard stays up to date for payroll and management.
**Independent Test**: Restore network connection after a period of offline clock-ins and verify that the logs appear in the central PostgreSQL database.

**Acceptance Scenarios**:
1. **Given** there are unsynced logs in the local DB, **When** connectivity is restored, **Then** the system batches and pushes them to the FastAPI ingestion endpoint.
2. **Given** a sync payload is sent, **When** the cloud backend verifies the NTP drift is within $\pm 5$ mins, **Then** the logs are successfully persisted to the cloud.

## Requirements *(mandatory)*

### Functional Requirements
- **FR-001**: System MUST use on-device AI (MediaPipe/Face Mesh) to detect head pose (Yaw/Pitch) in real-time and provide real-time feedback (e.g., "Too dark", "Turn more left") and stay on the current enrollment pose until a valid frame is captured.
- **FR-002**: System MUST capture images ONLY when quality thresholds (blur, illumination, pose) are met.
- **FR-003**: System MUST extract a 512-dimension biometric embedding for each enrollment angle.
- **FR-004**: System MUST index vectors using HNSW for $O(\log N)$ local search performance.
- **FR-005**: System MUST use an encrypted SQLite database for all local persistence.
- **FR-006**: System MUST implementation a Hardware Abstraction Layer (HAL) to support evaluation on a standard Laptop webcam.
- **FR-007**: System MUST sync logs in sequential chunks (e.g., 500 logs per request) via HTTPS POST with SHA-256 integrity verification.
- **FR-008**: System MUST identify the largest and most centered face in the frame as the Primary Face and focus all recognition logic solely on that target.
- **FR-009**: System MUST log a "Capture Failure" event and direct the user to "Consult Management" if environmental conditions consistently prevent a valid biometric capture ($>3$ consecutive failed attempts).

### Key Entities
- **Employee**: Represents the user; contains personal info and enrollment status.
- **BiometricTemplate**: The 512-d vector blob associated with an Employee.
- **AttendanceEvent**: A record of a clock-in/out (Timestamp, Employee_ID, Device_ID, Confidence_Score).
- **DeviceConfig**: Local settings for sync frequency, encryption keys, and HAL mode.

## Success Criteria *(mandatory)*

### Measurable Outcomes
- **SC-001**: On-device biometric matching latency MUST be $< 200\text{ms}$.
- **SC-002**: False Acceptance Rate (FAR) MUST be $< 0.001\%$.
- **SC-003**: System MUST retain 100% of attendance data during a simulated 30-day network blackout.
- **SC-004**: Enrollment completion rate for new users MUST be $> 95\%$ on the first attempt with guided prompts.
