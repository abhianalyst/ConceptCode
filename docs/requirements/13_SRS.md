# ConceptCode – AI Powered Adaptive Learning Platform
## Document 13: Software Requirement Specification (SRS)
**Version:** 1.0
**Phase:** Phase 0 – Requirement Analysis (Final Deliverable)
**Status:** Draft – Pending Final Approval
**Prepared By:** Development Team
**Date:** 2026-07-29
**Format Basis:** IEEE 830-1998 (adapted for an academic/MVP context)

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Overall Description](#2-overall-description)
3. [System Features (Functional Requirements Summary)](#3-system-features-functional-requirements-summary)
4. [External Interface Requirements](#4-external-interface-requirements)
5. [Non-Functional Requirements Summary](#5-non-functional-requirements-summary)
6. [Stakeholders and Users](#6-stakeholders-and-users)
7. [Use Case Summary](#7-use-case-summary)
8. [System Architecture Overview (Preview)](#8-system-architecture-overview-preview)
9. [Assumptions and Dependencies](#9-assumptions-and-dependencies)
10. [Constraints](#10-constraints)
11. [Risk Summary](#11-risk-summary)
12. [Success Criteria Summary](#12-success-criteria-summary)
13. [Appendices — Document Index](#13-appendices--document-index)
14. [Approval and Sign-Off](#14-approval-and-sign-off)

---

## 1. Introduction

### 1.1 Purpose
This Software Requirement Specification (SRS) formally defines the complete requirements for **ConceptCode v1.0**, an AI-powered adaptive learning platform for NEET exam preparation. It consolidates the full Phase 0 Requirement Analysis process (Documents 01–12) into a single authoritative specification, marking the transition point from **Phase 0: Requirement Analysis** to **Phase 1: System Design**.

### 1.2 Document Conventions
- Requirement IDs follow the format established across the prior 12 documents (e.g., `FR-XX-YY`, `NFR-CATEGORY-XX`).
- Priority levels: **High** (must-have for MVP), **Medium** (should-have), **Low** (nice-to-have, first to be cut under time pressure).
- This SRS is a **living reference to**, not a replacement for, Documents 01–12 — each section below summarizes and links back to the relevant full document for complete detail.

### 1.3 Intended Audience
| Audience | How They Use This Document |
|---|---|
| Development Team (both developers) | Primary build reference throughout Phases 1–5 |
| Project Guide / Faculty Mentor | Progress evaluation checkpoint |
| External Examiner / Evaluation Panel | Final assessment reference |
| Future Maintainers (v2.0+) | Onboarding reference for extending the platform |

### 1.4 Project Scope Statement
> ConceptCode v1.0 is a web-based, production-ready educational platform enabling NEET aspirants to practice adaptively, take realistic mock tests, resolve doubts and understand concepts via AI (Google Gemini), and receive machine-learning-driven weak-area insights — built by a 2-developer team within a 1-month timeline using Django, Django REST Framework, Scikit-Learn, and a Bootstrap-based frontend, deployed on Render with Neon PostgreSQL and Cloudinary.

Full scope boundary (in-scope vs. explicitly deferred features) is detailed in **Document 07: Project Scope**.

### 1.5 Definitions, Acronyms, and Abbreviations

| Term | Definition |
|---|---|
| NEET | National Eligibility cum Entrance Test |
| MVP | Minimum Viable Product |
| FR / NFR | Functional Requirement / Non-Functional Requirement |
| ML | Machine Learning |
| DRF | Django REST Framework |
| SRS | Software Requirement Specification |
| RTM | Requirement Traceability Matrix |
| PaaS | Platform as a Service |

---

## 2. Overall Description

### 2.1 Product Perspective
ConceptCode is a new, standalone product — not an extension of an existing system. It is a three-tier web application:

- **Presentation Tier:** Django templates + Bootstrap 5.3.8 + JavaScript + Chart.js
- **Application Tier:** Django + Django REST Framework (business logic, ML inference, AI orchestration)
- **Data Tier:** SQLite (development) / Neon PostgreSQL (production)

External systems integrated: **Google Gemini API** (AI tutoring), **Cloudinary** (media storage), **Render** (hosting).

### 2.2 Product Functions (High-Level Summary)
1. Student authentication and profile management
2. Structured syllabus navigation (Subjects → Chapters → Topics)
3. Adaptive, ML-driven practice sessions
4. Timed, NEET-format mock tests with detailed scoring
5. AI-powered doubt resolution (Gemini)
6. AI-powered concept explanation (Gemini)
7. Performance analytics and visualization
8. ML-based weak-area detection and recommendations
9. Study planning
10. Administrative content and user management
11. Engagement features: leaderboard, notifications

Full detail: **Document 01: Functional Requirements** (113 requirements across 14 modules).

### 2.3 User Classes and Characteristics

| User Class | Technical Proficiency | Primary Goal |
|---|---|---|
| Student | Low-Medium (general smartphone/laptop literacy) | Effective, personalized NEET preparation |
| Administrator | Medium (comfortable with web forms, spreadsheets) | Efficient content and user management |

Full persona detail (including behavioral profiles of three distinct student types): **Document 04: User Personas**.

### 2.4 Operating Environment
| Layer | Environment |
|---|---|
| Client | Modern web browsers (Chrome, Firefox, Edge, Safari — latest 2 versions), responsive from 320px to 1920px viewport width |
| Application Server | Render (Python/Django runtime) |
| Database (Dev) | SQLite |
| Database (Prod) | Neon PostgreSQL |
| Media Storage | Cloudinary |
| AI Provider | Google Gemini API |

### 2.5 Design and Implementation Constraints
The technology stack, UI design system, and team/timeline limitations are **fixed and non-negotiable**. Full detail: **Document 10: Constraints**. Summarized:
- Backend: Python, Django, Django REST Framework — mandatory
- Frontend: HTML5, CSS3, Bootstrap 5.3.8, JavaScript, Chart.js — mandatory, no alternative frameworks
- ML: NumPy, Pandas, Scikit-Learn, Joblib — classical ML only, no deep learning
- AI: Google Gemini API exclusively
- Team: 2 developers, 1 month, no dedicated QA/DevOps/design roles
- Design system: background `#E2ECF9`, cards `#FFFFFF`, accent `#1A1D24`, Poppins typography

### 2.6 Assumptions and Dependencies
Summarized in Section 9 of this document; full detail in **Document 09: Assumptions**.

---

## 3. System Features (Functional Requirements Summary)

This section summarizes the 14 functional modules. **Full requirement-level detail (all 113 FRs) is maintained in Document 01 and is considered part of this SRS by reference** — reproducing all 113 here would duplicate content without adding value; this SRS instead provides the module-level contract.

| # | Module | Description | Priority Weight | Full Detail |
|---|---|---|---|---|
| 1 | Authentication & User Management | Registration, login, verification, password reset, RBAC | High | Doc 01 §FR-01 |
| 2 | Student Dashboard | Personalized performance summary on login | High | Doc 01 §FR-02 |
| 3 | Subject/Topic Management | Structured NEET syllabus browsing | High | Doc 01 §FR-03 |
| 4 | Question Bank | Tagged, structured MCQ repository with admin CRUD | High | Doc 01 §FR-04 |
| 5 | Adaptive Practice Engine | Topic-wise practice with ML-driven difficulty | High | Doc 01 §FR-05 |
| 6 | Mock Test Module | Timed, NEET-format simulated exams | High | Doc 01 §FR-06 |
| 7 | AI Doubt Solver | Gemini-powered natural language Q&A | High | Doc 01 §FR-07 |
| 8 | AI Concept Explainer | Gemini-powered structured topic explanations | High | Doc 01 §FR-08 |
| 9 | Performance Analytics | Multi-dimensional visual performance breakdown | High | Doc 01 §FR-09 |
| 10 | Weak Area Detection (ML) | Scikit-Learn classification of topic strength | High | Doc 01 §FR-10 |
| 11 | Study Planner | Personal scheduling with auto-completion tracking | Medium | Doc 01 §FR-11 |
| 12 | Admin Panel | Content, user, and platform management | High | Doc 01 §FR-12 |
| 13 | Notifications | In-app milestone and update alerts | Medium | Doc 01 §FR-13 |
| 14 | Leaderboard | Competitive ranking by performance | Medium | Doc 01 §FR-14 |

**Total: 113 functional requirements** (67 High / 36 Medium / 10 Low priority) — see Document 01, Section 5 for the complete Requirement Traceability Matrix.

---

## 4. External Interface Requirements

### 4.1 User Interfaces
- All interfaces follow the fixed design system (Section 2.5) and must satisfy the "premium SaaS dashboard" qualitative standard: minimal, professional, responsive, modern, consistent (Document 10, CON-D-03).
- Full UI/UX success criteria: **Document 12, Section 6**.

### 4.2 Software Interfaces

| Interface | Purpose | Protocol/Method |
|---|---|---|
| Google Gemini API | AI doubt solving, concept explanation | REST API (HTTPS), server-side calls only |
| Cloudinary API | Image upload/storage (profile pictures, question images) | REST API / SDK |
| Neon PostgreSQL | Production data persistence | Django ORM over `psycopg`/PostgreSQL protocol |
| Render Platform | Application hosting and deployment | Git-based deployment, environment variable configuration |

### 4.3 Communications Interfaces
- All client-server communication over HTTPS/TLS (NFR-SEC-02).
- Email delivery for verification and password reset (provider to be selected in Phase 1 System Design — e.g., Django's SMTP backend or a transactional email service).

---

## 5. Non-Functional Requirements Summary

Full detail (62 requirements across 11 categories) is maintained in **Document 02: Non-Functional Requirements**. Summary by category:

| Category | Count | Representative Requirement |
|---|---|---|
| Performance | 7 | Dashboard loads in ≤3 seconds |
| Scalability | 4 | Supports 100 concurrent users for MVP |
| Security | 12 | Passwords hashed via PBKDF2; no secrets in source control |
| Reliability & Availability | 5 | 99% uptime during active hours; graceful AI failure handling |
| Usability | 8 | Fully responsive from 320px to 1920px |
| Maintainability | 8 | PEP 8 compliance; modular Django app structure |
| Portability & Compatibility | 3 | Cross-browser support (latest 2 versions of major browsers) |
| Data Requirements | 4 | UTC timestamp storage; cascading deletion on account removal |
| AI/ML Specific | 5 | ML inference <200ms; Gemini calls timeout at 10s with 1 retry |
| Cost Constraints | 3 | Operates within free/low-cost tiers of all third-party services |
| Compliance & Legal | 3 | DPDP Act 2023 alignment; Privacy Policy and ToS required |

---

## 6. Stakeholders and Users

Full detail: **Document 03: Stakeholders**. Summary:

| Category | Key Stakeholders |
|---|---|
| Primary (Direct Users) | Student, Administrator |
| Secondary (Governance) | Both Developers, Project Guide, External Examiner, Future Maintainers |
| Technical/External | Google Gemini API, Render, Neon PostgreSQL, Cloudinary, GitHub |
| Academic | Institution, Peer Students |

User personas (3 student archetypes + 1 admin archetype) driving design decisions throughout this specification are detailed in **Document 04: User Personas**.

---

## 7. Use Case Summary

Full detail (4 fully elaborated + 12 compact use cases): **Document 06: Use Cases**. The four highest-complexity use cases, fully specified with main/alternate/exception flows, are:

| Use Case | Core Risk Addressed |
|---|---|
| UC-01: Take a Mock Test | Server-authoritative timing, auto-save, idempotent submission |
| UC-02: Adaptive Practice Session | Real-time ML-driven difficulty adjustment, graceful fallback |
| UC-03: Ask the AI Doubt Solver | External API timeout/failure handling, rate limiting, content scope |
| UC-04: Weak Area Detection Update | Asynchronous, non-blocking ML processing with rule-based fallback |

User Stories with acceptance criteria (26 stories across 12 epics, 116 total story points) are detailed in **Document 05: User Stories**.

---

## 8. System Architecture Overview (Preview)

> This section is a **preview only**. Full architectural design — including entity-relationship diagrams, API endpoint specifications, ML pipeline design, and deployment architecture — is the deliverable of **Phase 1: System Design**, which begins immediately after this SRS is approved.

Based on the Feature List and Dependency Graph in **Document 08**, the system will be organized into modular Django apps, approximately:

```
conceptcode/
├── accounts/         (Auth, profiles, RBAC)
├── content/          (Subjects, Chapters, Topics, Questions)
├── practice/         (Adaptive Practice Engine)
├── mocktest/         (Mock Test Module)
├── ai_tutor/         (Gemini integration: Doubt Solver + Concept Explainer)
├── analytics/        (Performance aggregation and visualization)
├── ml_engine/        (Weak area detection, adaptive difficulty models)
├── planner/          (Study Planner)
├── engagement/       (Leaderboard, Notifications)
└── core/             (Shared utilities, base templates, design system)
```

This structure directly reflects the modular architecture mandated by **NFR-MAINT-01** and the dependency ordering established in **Document 08, Section 9**.

---

## 9. Assumptions and Dependencies

Full detail (27 assumptions across 6 categories, with a validation plan): **Document 09: Assumptions**. The most consequential (🔴 Critical impact) assumptions are:

| ID | Assumption | Validation Timing |
|---|---|---|
| AS-01, AS-02 | Team availability and technical proficiency are sufficient | Before Week 1 |
| AS-08 | Render free tier supports MVP-scale traffic | Week 1 |
| AS-13, AS-14 | Gemini API quota and answer quality are sufficient | Week 1 |
| AS-18, AS-19 | A legally-clean, sufficiently large question bank is achievable | Week 1 (parallel to development) |
| AS-27 | The 1-month timeline is fixed | Ongoing (governs Document 07 scope) |

---

## 10. Constraints

Full detail (7 categories: Time, Resource, Technology, Budget, Regulatory, Design): **Document 10: Constraints**. The most architecturally significant constraints are the mandated technology stack (Section 2.5 above) and the fixed 1-month/2-developer delivery window, which together justify the MVP scope boundary defined in **Document 07: Project Scope**.

---

## 11. Risk Summary

Full detail (16 identified risks, scored and mitigated): **Document 11: Risk Analysis**. The top risks requiring Week 1 action are:

| Risk | Score | Week 1 Action |
|---|---|---|
| Feature estimates prove optimistic | 9 | Track actual vs. estimated time from Day 1 |
| Question bank sourcing delay | 9 | Begin sourcing in parallel with development |
| Adaptive ML integration complexity | 6 | Build/test inference logic in isolation first |
| Mock test timer edge cases | 6 | Unit-test timer logic with short artificial durations |
| Team availability disruption | 6 | Build slack into Week 4; daily async check-ins |
| Gemini API quota insufficiency | 6 | Validate real quota; implement caching/rate-limiting early |
| Render cold-start demo impression | 6 | Warm up app before live evaluation |
| Insufficient ML training data | 6 | Generate synthetic training data early |
| Accidental API key leak | 6 | `.gitignore` and secret-scanning from first commit |

---

## 12. Success Criteria Summary

Full detail (8 categories, plus a Definition of Done and a final pre-submission checklist): **Document 12: Success Criteria**. The project is considered successful when:

1. All High-priority functional requirements are implemented, deployed, and verified (not just coded locally)
2. The ML weak-area model achieves ≥75% validation accuracy
3. AI features (Doubt Solver, Concept Explainer) function reliably with graceful failure handling
4. The platform is publicly deployed, responsive, and free of exposed secrets
5. The team can demonstrate the full product end-to-end in under 15 minutes
6. All scope decisions are traceable and defensible with reference to this documentation series

---

## 13. Appendices — Document Index

This SRS is the master document of Phase 0. The following documents are incorporated by reference in full:

| # | Document | Purpose |
|---|---|---|
| 01 | Functional Requirements | 113 detailed functional requirements across 14 modules |
| 02 | Non-Functional Requirements | 62 measurable quality attribute requirements |
| 03 | Stakeholders | Complete stakeholder register and engagement plan |
| 04 | User Personas | 4 detailed personas (3 students + 1 admin) |
| 05 | User Stories | 26 stories with acceptance criteria, story points, epics |
| 06 | Use Cases | 4 fully detailed + 12 compact use cases with exception flows |
| 07 | Project Scope | In-scope, out-of-scope, and simplified feature boundaries |
| 08 | Feature List | Build-ready feature inventory with dependency graph and 4-week plan |
| 09 | Assumptions | 27 assumptions with impact ratings and validation plan |
| 10 | Constraints | 7 categories of fixed project limitations |
| 11 | Risk Analysis | 16 scored risks with mitigation and contingency plans |
| 12 | Success Criteria | Measurable success definitions and final checklist |
| 13 | **This SRS** | Master consolidation and formal specification |

**All 13 documents together constitute the complete Phase 0: Requirement Analysis deliverable for ConceptCode v1.0.**

---

## 14. Approval and Sign-Off

This SRS, and the 12 supporting documents it consolidates, require review and approval before the project transitions to **Phase 1: System Design**.

| Role | Name | Approval Status | Date |
|---|---|---|---|
| Developer 1 | _____________ | ☐ Pending / ☐ Approved | _______ |
| Developer 2 | _____________ | ☐ Pending / ☐ Approved | _______ |
| Project Guide / Mentor | _____________ | ☐ Pending / ☐ Approved | _______ |

**Once signed off, this document is baselined.** Any future change follows the Change Control Process defined in Document 07, Section 8 — scope does not change silently mid-development.

---

## Document Control

| Field | Value |
|---|---|
| Document ID | CC-SRS-13 |
| Version | 1.0 |
| Created | 2026-07-29 |
| Last Updated | 2026-07-29 |
| Status | Draft — Pending Final Approval |
| Consolidates | CC-FRD-01 through CC-SUCCESS-12 |
| Storage Location | `docs/requirements/13_SRS.md` |
| Marks Completion Of | Phase 0: Requirement Analysis |
| Next Phase | Phase 1: System Design |

---

*End of Document — ConceptCode Software Requirement Specification v1.0*
*This document marks the formal conclusion of Phase 0: Requirement Analysis.*
