# ConceptCode – AI Powered Adaptive Learning Platform
## Document 02: Non-Functional Requirements
**Version:** 1.0
**Phase:** Phase 0 – Requirement Analysis
**Status:** Draft – Pending Review
**Prepared By:** Development Team
**Date:** 2026-07-29

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Performance Requirements](#2-performance-requirements)
3. [Scalability Requirements](#3-scalability-requirements)
4. [Security Requirements](#4-security-requirements)
5. [Reliability & Availability Requirements](#5-reliability--availability-requirements)
6. [Usability Requirements](#6-usability-requirements)
7. [Maintainability Requirements](#7-maintainability-requirements)
8. [Portability & Compatibility Requirements](#8-portability--compatibility-requirements)
9. [Data Requirements](#9-data-requirements)
10. [AI/ML Specific Non-Functional Requirements](#10-aiml-specific-non-functional-requirements)
11. [Cost Constraints](#11-cost-constraints)
12. [Compliance & Legal Requirements](#12-compliance--legal-requirements)
13. [NFR Summary Table](#13-nfr-summary-table)

---

## 1. Introduction

### 1.1 Purpose
This document specifies the quality attributes ConceptCode v1.0 must satisfy. Every requirement here is **measurable** — a good NFR is never vague ("the system should be fast"); it states a number, a condition, and a way to verify it.

### 1.2 Why Measurable NFRs Matter
"The system should be secure" cannot be tested. "Passwords shall be hashed using Django's PBKDF2 algorithm and never stored or logged in plaintext" can be tested — you either find plaintext passwords in the database or you don't. Every requirement below follows this principle.

---

## 2. Performance Requirements

| ID | Requirement | Target Metric |
|---|---|---|
| NFR-PERF-01 | Dashboard page shall load within an acceptable time under normal network conditions (3G/4G equivalent). | ≤ 3 seconds (first meaningful paint) |
| NFR-PERF-02 | Practice question submission (answer check) shall return a response quickly enough to not disrupt exam-like flow. | ≤ 1.5 seconds server response time |
| NFR-PERF-03 | Mock test timer shall remain accurate throughout the test duration with negligible client-server drift. | Drift ≤ 2 seconds over 200 minutes |
| NFR-PERF-04 | AI Doubt Solver response (Gemini API round trip) shall complete within a reasonable wait time, with a loading state shown throughout. | ≤ 8 seconds for 95% of requests |
| NFR-PERF-05 | Analytics charts (Chart.js) shall render after data fetch without noticeable UI freeze. | ≤ 1 second render time after data received |
| NFR-PERF-06 | Database queries powering the dashboard shall be optimized to avoid N+1 query problems. | Verified via Django Debug Toolbar; ≤ 10 queries per dashboard load |
| NFR-PERF-07 | Static assets (CSS, JS, images) shall be served efficiently. | Served via WhiteNoise/Cloudinary with compression enabled |

**Why these numbers?** These targets are based on published UX research: users perceive a wait as "instant" up to ~1 second, and abandon a task if it takes longer than ~3-4 seconds without feedback. The AI response threshold (8s) is deliberately more lenient because users mentally categorize "asking an AI a question" differently from "clicking a button" — but a loading indicator is mandatory to manage that expectation (see FR-07-05).

---

## 3. Scalability Requirements

| ID | Requirement | Target Metric |
|---|---|---|
| NFR-SCALE-01 | The system shall support a minimum number of concurrent active users for the MVP without performance degradation. | 100 concurrent users |
| NFR-SCALE-02 | The database schema shall be designed to scale to a defined question bank size without requiring redesign. | Up to 50,000 questions |
| NFR-SCALE-03 | The system architecture shall allow horizontal scaling of the web layer (stateless Django app servers) if traffic grows post-MVP. | Documented as future capability, not required to be load-tested for v1.0 |
| NFR-SCALE-04 | Database connection pooling shall be configured to handle Render + Neon PostgreSQL's connection limits gracefully. | No connection-limit errors under 100 concurrent users |

**Why 100 concurrent users?** This is a Final Year Project MVP, not a commercial product day one. 100 concurrent users is a realistic, defensible target for an academic evaluation and initial pilot launch, while still requiring you to design responsibly (avoiding query traps, using indexes, etc.) rather than writing throwaway code.

---

## 4. Security Requirements

| ID | Requirement |
|---|---|
| NFR-SEC-01 | All passwords shall be hashed using Django's default PBKDF2-SHA256 algorithm; plaintext passwords shall never be stored, logged, or transmitted. |
| NFR-SEC-02 | All data in transit shall be encrypted via HTTPS/TLS (enforced at the Render deployment layer). |
| NFR-SEC-03 | The system shall implement Django's CSRF protection on all state-changing forms and API endpoints. |
| NFR-SEC-04 | The system shall implement Django REST Framework's authentication (Token or Session-based) on all API endpoints. |
| NFR-SEC-05 | The system shall sanitize and validate all user input to prevent SQL Injection (mitigated by Django ORM usage) and Cross-Site Scripting (XSS). |
| NFR-SEC-06 | Environment variables (API keys, database credentials, secret keys) shall never be committed to version control; a `.env` file (git-ignored) and Render's environment variable manager shall be used. |
| NFR-SEC-07 | The Google Gemini API key shall be stored server-side only and never exposed to the client/browser. |
| NFR-SEC-08 | The system shall implement role-based access control (RBAC) distinguishing Student and Administrator permissions at the view/permission-class level. |
| NFR-SEC-09 | Session cookies shall be marked `HttpOnly` and `Secure` in production settings. |
| NFR-SEC-10 | The system shall rate-limit login attempts (see FR-01-12) and AI API calls per user to prevent abuse (max 30 AI requests/hour/user). |
| NFR-SEC-11 | File uploads (profile pictures, question images) shall be restricted by file type (JPEG/PNG only) and size (≤ 5MB), validated server-side. |
| NFR-SEC-12 | `DEBUG = False` shall be enforced in the production Django settings, with a custom 404/500 error page. |

**Why is this section so detailed compared to others?** Security is the NFR category most commonly under-documented in student projects, and it's the one evaluators and real-world employers scrutinize hardest. Storing an AI API key in a `views.py` file that gets pushed to a public GitHub repo is a mistake made by beginners and professionals alike — documenting it here as a hard requirement makes it a checklist item, not an afterthought.

---

## 5. Reliability & Availability Requirements

| ID | Requirement | Target Metric |
|---|---|---|
| NFR-REL-01 | The platform shall target a defined uptime during the evaluation/demo period, acknowledging Render free-tier limitations (cold starts). | 99% uptime during active hours (excluding planned maintenance) |
| NFR-REL-02 | If the Gemini API is unavailable or errors out, the system shall degrade gracefully with a clear user-facing message rather than crashing. | 100% of AI failures caught and handled (no unhandled 500 errors) |
| NFR-REL-03 | Mock test progress shall be periodically auto-saved to prevent data loss from browser crashes or network drops. | Auto-save every 30 seconds during an active test |
| NFR-REL-04 | Database backups shall be taken regularly to prevent data loss (Neon PostgreSQL automated backups). | Daily automated backup (Neon default retention) |
| NFR-REL-05 | The system shall log all unhandled exceptions server-side for debugging without exposing stack traces to end users. | Django logging configured; no stack traces in production responses |

---

## 6. Usability Requirements

| ID | Requirement |
|---|---|
| NFR-USE-01 | The UI shall follow the specified design system: background `#E2ECF9`, card surfaces `#FFFFFF`, primary accent `#1A1D24`, and Poppins typography throughout. |
| NFR-USE-02 | The interface shall be fully responsive, functioning correctly on screen widths from 320px (mobile) to 1920px (desktop), using Bootstrap 5.3.8's grid system. |
| NFR-USE-03 | All interactive elements (buttons, links, form fields) shall have a minimum touch target size of 44x44px for mobile usability. |
| NFR-USE-04 | The system shall provide clear, immediate visual feedback for all user actions (loading spinners, success/error toasts, disabled states during submission). |
| NFR-USE-05 | Error messages shall be human-readable and actionable (e.g., "Password must be at least 8 characters" rather than a raw exception). |
| NFR-USE-06 | Critical user flows (registration, starting a practice session, starting a mock test) shall require no more than 3 clicks from the dashboard. |
| NFR-USE-07 | The system shall maintain consistent navigation (a persistent sidebar/navbar) across all authenticated pages. |
| NFR-USE-08 | Forms shall provide inline, real-time validation feedback where feasible (e.g., password strength, email format). |

---

## 7. Maintainability Requirements

| ID | Requirement |
|---|---|
| NFR-MAINT-01 | The codebase shall follow Django's app-based modular architecture — each major feature (accounts, practice, tests, ai_tutor, analytics) shall be a separate Django app. |
| NFR-MAINT-02 | All Python code shall follow PEP 8 style guidelines. |
| NFR-MAINT-03 | All models, views, and non-trivial functions shall include docstrings explaining their purpose. |
| NFR-MAINT-04 | The project shall maintain a `requirements.txt` (or `pyproject.toml`) with pinned dependency versions to ensure reproducible environments. |
| NFR-MAINT-05 | Environment-specific settings (development vs. production) shall be separated using Django settings modules or environment variables — never hardcoded. |
| NFR-MAINT-06 | The project shall use Git with a clear branching strategy (`main`, `develop`, feature branches) and descriptive commit messages. |
| NFR-MAINT-07 | Reusable UI components (cards, buttons, chart containers) shall be implemented as Django template partials/includes to avoid duplication. |
| NFR-MAINT-08 | The ML model training pipeline shall be a separate, documented, re-runnable script — not embedded inline in application views. |

---

## 8. Portability & Compatibility Requirements

| ID | Requirement |
|---|---|
| NFR-PORT-01 | The web application shall function correctly on the latest two versions of Chrome, Firefox, Edge, and Safari. |
| NFR-PORT-02 | The system shall be developed against SQLite locally and PostgreSQL (Neon) in production, using Django ORM exclusively (no raw SQL that is database-specific). |
| NFR-PORT-03 | The application shall be containerizable in principle (clear dependency list, no hardcoded local file paths) even if Docker is not used for v1.0 deployment. |

---

## 9. Data Requirements

| ID | Requirement |
|---|---|
| NFR-DATA-01 | Student performance data shall be retained indefinitely to support long-term analytics, unless the student requests account deletion. |
| NFR-DATA-02 | Deleted user accounts shall trigger cascading anonymization or deletion of personally identifiable information within 30 days. |
| NFR-DATA-03 | All timestamps shall be stored in UTC and converted to the user's local timezone for display. |
| NFR-DATA-04 | Question bank data integrity shall be enforced via database constraints (e.g., a question must have exactly one correct answer, foreign keys to valid topics). |

---

## 10. AI/ML Specific Non-Functional Requirements

| ID | Requirement |
|---|---|
| NFR-AI-01 | The adaptive difficulty ML model shall be retrained on a defined schedule (e.g., weekly batch job) rather than in real-time per request, to keep inference fast. |
| NFR-AI-02 | ML model inference (predicting weak areas / next difficulty) shall complete in under 200ms per request. |
| NFR-AI-03 | The Gemini API integration shall implement a request timeout (10 seconds) and a single retry on transient failure before surfacing an error to the user. |
| NFR-AI-04 | AI-generated content (doubt answers, concept explanations) shall be clearly labeled as "AI-generated" in the UI to maintain transparency with students. |
| NFR-AI-05 | The system shall log Gemini API usage (request count, approximate token usage) to support cost monitoring. |

---

## 11. Cost Constraints

| ID | Requirement |
|---|---|
| NFR-COST-01 | The MVP shall be deployable using free or low-cost tiers of Render, Neon PostgreSQL, and Cloudinary to keep the project financially viable for a student team. |
| NFR-COST-02 | Gemini API usage shall be monitored and rate-limited per user (see NFR-SEC-10) to avoid unexpected billing spikes. |
| NFR-COST-03 | Caching (see FR-08-05) shall be used to reduce redundant, billable AI API calls wherever content is reusable across students. |

**Why include cost as a formal NFR?** Many student projects ignore operational cost entirely and are shocked when a demo goes viral or an API key gets abused, generating a large bill. Treating cost as a first-class non-functional requirement — the same way a real startup would — is part of building professional habits early.

---

## 12. Compliance & Legal Requirements

| ID | Requirement |
|---|---|
| NFR-LEGAL-01 | The platform shall display a Privacy Policy and Terms of Service, disclosing what student data is collected and how it is used. |
| NFR-LEGAL-02 | Since ConceptCode targets Indian students preparing for NEET, the platform shall align with applicable Indian data protection principles under the Digital Personal Data Protection Act (DPDP), 2023 — specifically around consent and data minimization. |
| NFR-LEGAL-03 | Question content sourced from previous NEET papers shall be used strictly for educational purposes; original questions and copyrighted third-party material shall not be reproduced without appropriate rights. |

---

## 13. NFR Summary Table

| Category | Total Requirements | Priority Focus |
|---|---|---|
| Performance | 7 | High — directly impacts exam-like UX |
| Scalability | 4 | Medium — MVP scale, designed for growth |
| Security | 12 | High — non-negotiable, data privacy |
| Reliability & Availability | 5 | High — especially AI failure handling |
| Usability | 8 | High — design system compliance |
| Maintainability | 8 | High — 2-developer team needs clean architecture |
| Portability & Compatibility | 3 | Medium |
| Data Requirements | 4 | Medium |
| AI/ML Specific | 5 | High — core differentiator of the product |
| Cost Constraints | 3 | High — student project budget reality |
| Compliance & Legal | 3 | Medium — required for a real-facing platform |
| **TOTAL** | **62** | — |

---

## Document Control

| Field | Value |
|---|---|
| Document ID | CC-NFR-02 |
| Version | 1.0 |
| Created | 2026-07-29 |
| Last Updated | 2026-07-29 |
| Status | Draft |
| Depends On | CC-FRD-01 (Functional Requirements) |
| Storage Location | `docs/requirements/02_non_functional_requirements.md` |

---

*End of Document — ConceptCode Non-Functional Requirements v1.0*
