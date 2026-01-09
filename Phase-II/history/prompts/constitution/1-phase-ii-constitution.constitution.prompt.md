---
id: 1
title: Phase II Constitution Definition
stage: constitution
date: 2026-01-09
surface: agent
model: claude-haiku-4-5-20251001
feature: none
branch: main
user: Ahad
command: /sp.constitution
labels: ["phase-ii", "governance", "sdd", "security", "architecture"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - Constitution file created with no unresolved placeholders
  - All principles clearly defined with rationale
  - Security requirements explicitly stated
  - Version 1.0.0 set with ratification date
---

## Prompt

Project: Todo Full-Stack Web Application (Hackathon 2 – Phase II)

Purpose:
Transform the Phase I in-memory console Todo app into a secure, multi-user, full-stack web application with persistent storage, following strict spec-driven development.

Core Principles:
- Spec-Driven Development: All work must follow approved specifications
- Correctness: Features must behave exactly as specified
- Security by Design: Authentication and user isolation are mandatory
- Separation of Concerns: Frontend, backend, database, and auth clearly separated
- Evolvability: Architecture must support future phases without redesign

Key Standards:
- All features traceable to specs in `/specs/`
- REST APIs follow defined contracts and HTTP semantics
- Each user can access only their own data
- Authentication enforced on every API request
- Frontend and backend must verify JWT consistently
- Monorepo structure must be respected

Technical Constraints:
- Frontend: Next.js 16+ (App Router)
- Backend: FastAPI (Python)
- ORM: SQLModel
- Database: Neon Serverless PostgreSQL
- Authentication: Better Auth with JWT
- Spec-Driven: Claude Code + Spec-Kit Plus only
- No manual coding

Security Requirements:
- All API routes require valid JWT token
- JWT verified using shared secret (BETTER_AUTH_SECRET)
- User identity derived from token, not client input
- Task ownership enforced on all CRUD operations
- Unauthorized requests return 401

Authentication & Identity:
- User authentication is required for all application features
- Better Auth is used for signup, login, logout, and session management
- Authentication is JWT-based
- JWT is verified on every backend request
- User identity is derived exclusively from the verified token
- All data access is scoped to the authenticated user

Repository & Spec Structure:
- Monorepo layout as defined in Spec-Kit configuration
- Specs organized under `/specs/` by feature, API, database, and UI
- Root and scoped CLAUDE.md files must guide implementation
- Frontend and backend code isolated in `/frontend` and `/backend`

Constraints:
- Phase II scope only (no chatbot, no Kubernetes, no streaming)
- No undocumented endpoints or features
- No cross-user data access
- No deviation from approved API and database specs

Success Criteria:
- All 5 basic Todo features work via web UI
- REST API fully functional and secured with JWT
- Tasks persist in Neon PostgreSQL
- Each user sees and modifies only their own tasks
- Repository structure, specs, and code are consistent
- Project is ready to evolve into Phase III without refactoring

## Response snapshot

Constitution created with 5 core principles (Spec-Driven Development, Security by Design, Separation of Concerns, Correctness Over Cleverness, Evolvability). Added sections for Technical Constraints, Security Requirements, Authentication & Identity, Repository & Spec Structure, Constraints & Non-Goals, Success Criteria, and Governance. Version set to 1.0.0, ratified 2026-01-09. All placeholders resolved.

## Outcome

- ✅ Impact: Phase II governance foundation established; all development must align with constitution principles
- 🧪 Tests: Constitution file validated with no unresolved placeholders; all sections complete and coherent
- 📁 Files: .specify/memory/constitution.md created and filled (version 1.0.0)
- 🔁 Next prompts: Create feature specs for auth, todo-api, database, and frontend; then plan Phase II architecture
- 🧠 Reflection: Constitution emphasizes spec-driven approach, security-first mindset, and multi-user isolation—ready to guide all subsequent development

## Evaluation notes (flywheel)

- Failure modes observed: None; constitution template replaced entirely with project-specific content
- Graders run and results (PASS/FAIL): PASS - all placeholders filled, version coherent, ratification date valid
- Prompt variant (if applicable): Initial constitution creation (no prior version)
- Next experiment (smallest change to try): Create specs for core features (auth, todo-api, database)
