# Research & Decision Log: Phase 2 - Bilingual UI/UX & Governance

## RD-001: Bilingual UI & RTL Mirroring (Dashboard)

- **Decision**: Use `next-intl` for internationalization and Tailwind CSS Logical Properties for RTL mirroring.
- **Rationale**: `next_intl` provides server-side locale detection and seamless integration with Next.js App Router. Tailwind Logical Properties (e.g., `start`, `end`, `ms-`, `me-`) allow a single CSS codebase to support both LTR and RTL without manual overrides.
- **Alternatives Considered**: 
  - `react-i18next`: Powerful but slightly heavier configuration for Next.js App Router.
  - Manual CSS `[dir="rtl"]` overrides: Harder to maintain and prone to layout bugs.

## RD-002: Maker-Checker Governance (Cloud)

- **Decision**: Implement a centralized `approval_requests` table using PostgreSQL `JSONB` for change payloads.
- **Rationale**: `JSONB` allows flexibility in storing diffs for different entities (Employees, Biometrics, Sites) without complex schema migrations. A generic state machine (`PENDING` -> `APPROVED`/`REJECTED`) ensures consistent audit trails across the system.
- **Security Check**: FastAPI middleware will enforce `maker_id != checker_id` at the API level.

## RD-003: Localized Audio Engine (Edge)

- **Decision**: Use `pygame.mixer` for playback of pre-recorded `.wav` files.
- **Rationale**: `pygame` is lightweight and highly reliable for offline playback on Linux/Windows. Using pre-recorded studio-quality Arabic/English prompts ensures a premium "inclusive" feel compared to robotic TTS.
- **Smart Logic**: A 3-second "Stall Timer" will be added to the recognition loop; if no match is found and the face is detected, a guidance prompt (e.g., "Move Closer") will trigger.

## RD-004: IP Allow-listing (Security)

- **Decision**: Store a list of CIDR blocks in the `tenants` table and implement a global FastAPI Middleware for IP verification.
- **Rationale**: CIDR support allows clients to allow-list entire office ranges. Middle-ware enforcement ensures security is "Always On" for administrative endpoints without polluting business logic.
