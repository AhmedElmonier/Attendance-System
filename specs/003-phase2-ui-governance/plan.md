# Implementation Plan: Phase 2 - Bilingual UI/UX & Governance

**Branch**: `003-phase2-ui-governance` | **Date**: 2026-03-22 | **Spec**: [spec.md](file:///d:/Projects/Attendance-System/specs/003-phase2-ui-governance/spec.md)
**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Phase 2 focuses on delivering a production-ready **Bilingual Management Dashboard (AR/EN)** and a robust **Governance (Maker-Checker)** framework. This ensures the system is not only usable by the Egyptian workforce but also meets enterprise-grade security standards for biometric data integrity.

## Technical Context

**Language/Version**: Python 3.9+ (Edge/Cloud), TypeScript 5.0+ (Next.js Dashboard)  
**Primary Dependencies**: `next-intl`, Tailwind CSS (Logical Properties), `fastapi`, `sqlcipher3`  
**Storage**: PostgreSQL (Cloud) with RLS, SQLite/SQLCipher (Edge)  
**Testing**: `pytest` (API/Edge), `playwright` (UI/i18n/RTL)  
**Target Platform**: Web (Chrome/Edge/Safari), Windows/Linux (Edge Device)
**Project Type**: Web Service + IoT Edge Node  
**Performance Goals**: < 100ms Recognition Feedback, < 1s Audit/Approval retrieval  
**Constraints**: Full RTL Mirroring, Maker-Checker isolation, 4k/Touch-ready Kiosk UI  
**Scale/Scope**: Enterprise multi-tenant (100+ sites per tenant)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. Privacy & Compliance**: [PASS] Biometric re-enrollment requires a second Admin approval (Maker-Checker).
- **II. Edge-First Resilience**: [PASS] Smart Audio Guidance & localized UI pre-cached on edge for zero-latency offline feedback.
- **III. Bilingual & Inclusive UX**: [PASS] Mandatory AR/EN support with RTL mirroring across all dashboard and kiosk screens.
- **IV. Hardware Abstraction (HAL)**: [PASS] Kiosk UI built with Flutter/Web to facilitate simulation on Laptop/WSL2.
- **V. Multi-Tenant Security**: [PASS] IP Allow-listing and strict self-approval restrictions for cross-tenant administration.

## Project Structure

### Documentation (this feature)

```text
specs/003-phase2-ui-governance/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── governance_api.md
└── tasks.md             # Phase 2 output (Future)
```

### Source Code (repository root)

```text
cloud/
├── src/
│   ├── api/
│   │   ├── governance.py    # NEW: Approvals & Audit
│   │   └── middleware/
│   │       └── ip_filter.py # NEW: Allow-listing logic
│   └── models/
│       ├── approval.py      # NEW: Pydantic/SQLAlchemy
│       └── audit.py         # NEW: Pydantic/SQLAlchemy
└── tests/
    └── integration/
        └── test_governance.py

dashboard/
├── messages/                # NEW: en.json, ar.json
├── src/
│   ├── components/
│   │   └── i18n/            # NEW: Switcher & Logic
│   └── layout.tsx           # MOD: RTL/LTR Logic
└── tests/
    └── e2e/
        └── test_i18n.spec.ts

edge/
├── src/
│   └── audio/               # NEW: Audio engine
└── assets/
    └── audio/               # NEW: .wav prompts
```

**Structure Decision**: Selected a **Web + Edge Hybrid** structure to accommodate the parallel development of the Cloud governance API, the Next.js dashboard, and the Python-based edge audio engine.

## Verification Plan

### Automated Tests

1. **Governance API Unit Tests (Pytest)**:
   - Command: `pytest cloud/tests/integration/test_governance.py`
   - Scenarios: Create approval, Prevent self-approval (403), Approve as separate user, Verify Audit record creation.

2. **Dashboard i18n E2E Tests (Playwright)**:
   - Command: `npx playwright test dashboard/tests/e2e/test_i18n.spec.ts`
   - Scenarios: Toggling locales, verifying `dir="rtl"` application, checking label translations.

3. **IP Allow-listing Middleware Test**:
   - Command: `pytest cloud/tests/unit/test_ip_filter.py`
   - Scenarios: Match against CIDR block, Reject unauthorized IP, Pass authorized IP.

### Manual Verification

1. **Edge Audio Simulation**: 
   - Run `python edge/tests/simulate_audio.py`.
   - Action: Manually verify that the "Success" sound plays on a match and that "Guidance" triggers after 3 seconds of stagnation.
2. **Side-by-Side Diff Review**:
   - Navigate to the Dashboard -> Approvals.
   - Action: Confirm that two face images (Old/New) are displayed clearly for decision making.
