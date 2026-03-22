# Feature Specification: Phase 3 - Advanced Security & Mobile

**Feature Branch**: `004-advanced-security-mobile`  
**Created**: 2026-03-22  
**Status**: Draft  
**Input**: User description: "Implement cryptographically signed vector purges, periocular recognition fallback, AES-256 backup engine, and a Flutter-based Mobile Manager app with push alerts."

## Clarifications

### Session 2026-03-22
- Q: What is the intended scope/granularity of the "Wipe Vector" command? → A: Full Device Wipe (all tenants/users on the kiosk).
- Q: Should Site Managers provide a mandatory reason for manual overrides? → A: Mandatory Text (brief reason must be typed).
- Q: What should be the lockout behavior after 3 failures? → A: Temporary Lockout (60s) AND ID-Entry Fallback.
- Q: What is the backup frequency and storage location? → A: Daily (Off-site Cloud Storage).
- Q: What is the required backup retention period? → A: 30 Days.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Remote Biometric Purge (Priority: P1)

As a Cloud Administrator, I want to issue a securely signed "Wipe Vector" command to a specific Edge Kiosk (or all kiosks) so that all sensitive biometric data for all users and tenants is immediately and irrecoverably deleted in case of device theft or node decommissioning.

**Why this priority**: Critical for GDPR/privacy compliance and hardware security. Data must not be retrievable if the physical device is compromised.

**Independent Test**: Can be tested by issuing a signed instruction from the Cloud and verifying that the local matching index and biometric data on the edge device are deleted and overwritten.

**Acceptance Scenarios**:

1.  **Given** a kiosk is online and synced, **When** a "Wipe" command is broadcast with a valid secure signature, **Then** the kiosk must delete all local biometric templates within 5 seconds and report "Purge Complete".
2.  **Given** a kiosk is offline, **When** it reconnects, **Then** it must immediately process any pending signed "Wipe" commands before resuming attendance matching.

---

### User Story 2 - Mobile Alert & Override (Priority: P1)

As a Site Manager, I want to receive a push notification on my mobile app when an "Unverified" attendance event occurs (e.g., matching confidence < 85%) so that I can see the person's photo and manually approve/override the entry in real-time.

**Why this priority**: Reduces friction for legitimate employees who fail biometric matching (e.g., due to temporary injury or lighting) and provides immediate oversight.

**Independent Test**: Simulate a low-confidence match on a Kiosk, verify a push notification arrives on the Flutter Mobile App within 2 seconds, and verify that tapping "Approve" updates the Cloud record and signals the Kiosk.

**Acceptance Scenarios**:

1. **Given** an "Unverified" event on the edge, **When** the event is synced to the cloud, **Then** a push notification must be sent to all Managers assigned to that site.
2. **Given** a manager views the alert, **When** they approve the manual override, **Then** they MUST provide a mandatory text reason before the action is permanent, and the employee must be marked as "Present (Manual Override)" in the attendance logs.

---

### User Story 3 - Periocular Recognition Fallback (Priority: P2)

As an Employee wearing a medical mask or niqab, I want the Kiosk to recognize me based on the area around my eyes (periocular) so that I don't have to remove my face covering during the attendance process.

**Why this priority**: Essential for inclusivity and cultural requirements in the Egyptian market, and for health compliance during outbreaks.

**Independent Test**: An enrolled user wears a opaque medical mask covering the mouth and nose; verify the system achieves a match with >90% confidence using only the ocular region.

**Acceptance Scenarios**:

1. **Given** the lower face is obscured, **When** the employee looks at the camera, **Then** the system must automatically switch to a periocular model or weight for the eye region.
2. **Given** a niqab is worn, **When** matching occurs, **Then** the system must maintain the same <200ms latency requirement.

---

### User Story 4 - High-Security Encrypted Backups (Priority: P2)

As a System Auditor, I want the system to perform automated, encrypted backups of the Cloud database using AES-256 and Argon2id, so that data remains secure even if the storage provider is compromised.

**Why this priority**: Prevents "Trapdoor" access to sensitive attendance data in case of infrastructure breach.

**Independent Test**: Trigger a backup, download the artifact, and verify it cannot be decrypted without the separate, externally managed master key.

**Acceptance Scenarios**:

1. **Given** a daily automated schedule, **When** the engine runs, **Then** all tables must be dumped, encrypted, and transferred to a physically separate cloud storage region with a 30-day retention policy.
2. **Given** the backup is stored, **When** it is retrieved, **Then** it must pass an integrity check (HMAC/Signature) before decryption is allowed.

### Edge Cases

- **Mobile App Connectivity**: What happens if the Manager is in a dead zone when an override is needed? (Resolved: The event remains "Unverified" until approved via the web dashboard or mobile app later; the kiosk does not "Auto-Approve").
- **Clock Drift during Purge**: How does the system prevent replay attacks on the "Wipe" command? (Resolved: Signed purge commands must include a millisecond-precision timestamp and have a validity window of < 60 seconds).
- **Multiple Overrides**: Two managers try to override the same event simultaneously. (Resolved: First action wins; the second attempt receives a "Request already processed" alert).
- **Multi-Failure Lockout**: A user fails 3 consecutive matching attempts. (Resolved: Kiosk locks matching for 60 seconds, alerts the Site Manager, and offers an 'Enter ID' fallback button for manual review).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST support securely signed commands delivered via real-time remote communication for administrative edge operations.
- **FR-002**: Edge Kiosks MUST perform a "Secure Delete" (overwriting sectors) of all local biometric templates (Full Device Wipe) when the Wipe command is verified.
- **FR-003**: The Vision Pipeline MUST include a ROI (Region of Interest) focus for periocular matching when detection indicates the mouth/nose are obscured.
- **FR-004**: System MUST perform automated daily backups, encrypted using industry-standard authenticated encryption, and stored in an off-site cloud object store with a 30-day rolling retention policy.
- **FR-005**: The Mobile App MUST support standard push notification services for both Android and iOS platforms.
- **FR-006**: The Mobile App MUST provide a real-time feed of "Unverified" events limited to the Manager's assigned tenants/sites.
- **FR-007**: System MUST log every manual override (who approved, when, the mandatory reason provided, and from which device) in the Audit Trail.
- **FR-008**: System MUST implement a 60-second lockout on the Kiosk after 3 consecutive matching failures for a single user interaction.
- **FR-009**: Kiosk MUST provide an manual ID-entry fallback option after a lockout, which triggers an "Unverified" event for Site Manager review.

### Key Entities *(include if feature involves data)*

- **WipeCommand**: Represents a signed administrative instruction (command_id, timestamp, signature, target_id).
- **MobileDevice**: Represents a registered mobile instance for push notifications (fcm_token, user_id, OS_type).
- **EncryptedBackup**: Metadata for a backup artifact (storage_path, checksum, encryption_version).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of signed "Wipe" commands must be executed by an online Kiosk within < 5 seconds of receipt.
- **SC-002**: Periocular recognition MUST achieve >95% accuracy for users with 75% of the face obscured (medical masks).
- **SC-003**: Push notifications MUST be delivered to mobile devices within < 3 seconds of the "Unverified" event being recorded in the cloud.
- **SC-004**: Decryption of a standard 1GB backup must be completed in < 60 seconds on standard environments once the authorized key is provided.
- **SC-005**: Mobile app must maintain >99.9% crash-free sessions for Site Managers.
