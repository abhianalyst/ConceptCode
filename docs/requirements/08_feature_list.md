# ConceptCode – AI Powered Adaptive Learning Platform
## Document 08: Feature List
**Version:** 1.0
**Phase:** Phase 0 – Requirement Analysis
**Status:** Draft – Pending Review
**Prepared By:** Development Team
**Date:** 2026-07-29

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Feature List Legend](#2-feature-list-legend)
3. [Foundation Layer Features](#3-foundation-layer-features)
4. [Core Learning Features](#4-core-learning-features)
5. [AI-Powered Features](#5-ai-powered-features)
6. [Analytics & Intelligence Features](#6-analytics--intelligence-features)
7. [Engagement Features](#7-engagement-features)
8. [Administration Features](#8-administration-features)
9. [Dependency Graph](#9-dependency-graph)
10. [Suggested Build Order (4-Week Plan)](#10-suggested-build-order-4-week-plan)

---

## 1. Introduction

### 1.1 Purpose
This document lists every feature committed for ConceptCode v1.0, each tagged with complexity, dependencies, and the module it belongs to, to directly support sprint planning and task assignment across the 2-developer team.

### 1.2 Relationship to Prior Documents
This is a **derived document** — every row traces back to Document 01 (FRs), is scoped by Document 07 (Project Scope), and is sized by Document 05 (Story Points). No new requirements are introduced here.

---

## 2. Feature List Legend

| Complexity | Meaning |
|---|---|
| 🟢 Low | Standard CRUD or UI work; well-understood Django patterns |
| 🟡 Medium | Involves business logic, multiple models, or non-trivial UI state |
| 🔴 High | Involves external integration (AI/ML), real-time constraints, or complex state management |

---

## 3. Foundation Layer Features

*Must be built first — nothing else functions without these.*

| Feature | Module | Complexity | Depends On | Linked FR |
|---|---|---|---|---|
| User registration with email verification | Auth | 🟡 Medium | None | FR-01-01 to FR-01-05 |
| Login / Logout | Auth | 🟢 Low | Registration | FR-01-06, FR-01-10 |
| Password reset flow | Auth | 🟡 Medium | Registration | FR-01-07 |
| User profile management | Auth | 🟢 Low | Login | FR-01-08, FR-01-09 |
| Role-based access control (Student/Admin) | Auth | 🟡 Medium | Registration | NFR-SEC-08 |
| Subject/Chapter/Topic data models | Content | 🟢 Low | None | FR-03-01 to FR-03-03 |
| Syllabus explorer UI | Content | 🟡 Medium | Subject/Chapter/Topic models | FR-03-04 to FR-03-07 |
| Question Bank data model | Content | 🟡 Medium | Subject/Chapter/Topic models | FR-04-01 to FR-04-03 |
| Admin CRUD for questions | Content | 🟡 Medium | Question Bank model | FR-04-05 |
| Base UI layout, navbar, sidebar (design system) | UI | 🟡 Medium | None | NFR-USE-01, NFR-USE-07 |

---

## 4. Core Learning Features

*The primary value-delivery features of the platform.*

| Feature | Module | Complexity | Depends On | Linked FR |
|---|---|---|---|---|
| Practice session engine (question serving, answer eval) | Practice | 🟡 Medium | Question Bank | FR-05-01, FR-05-02, FR-05-04, FR-05-05 |
| Adaptive difficulty logic (ML-driven) | Practice | 🔴 High | Practice engine, ML model | FR-05-03 |
| Session pause/resume | Practice | 🟡 Medium | Practice engine | FR-05-09 |
| Session summary screen | Practice | 🟢 Low | Practice engine | FR-05-10 |
| Question bookmarking | Practice | 🟢 Low | Practice engine | FR-05-06 |
| Mock test generator (question selection logic) | Mock Test | 🟡 Medium | Question Bank | FR-06-01, FR-06-02 |
| Mock test timer (server-authoritative) | Mock Test | 🔴 High | Mock test generator | FR-06-03 |
| Mock test interface (palette, navigation, marking) | Mock Test | 🔴 High | Mock test generator | FR-06-05, FR-06-06 |
| NEET marking scheme scoring engine | Mock Test | 🟡 Medium | Mock test interface | FR-06-04 |
| Mock test result report generation | Mock Test | 🟡 Medium | Scoring engine | FR-06-07 |
| Mock test history view | Mock Test | 🟢 Low | Result report | FR-06-09 |
| Auto-save during mock test | Mock Test | 🟡 Medium | Mock test interface | NFR-REL-03 |

---

## 5. AI-Powered Features

*Core differentiators justifying the "AI Powered" claim in the project name.*

| Feature | Module | Complexity | Depends On | Linked FR |
|---|---|---|---|---|
| Gemini API integration layer (base service class) | AI Core | 🔴 High | None | NFR-AI-03, NFR-SEC-07 |
| AI Doubt Solver UI + query flow | AI Doubt | 🟡 Medium | Gemini integration layer | FR-07-01 to FR-07-05 |
| Doubt history storage and view | AI Doubt | 🟢 Low | AI Doubt Solver | FR-07-06, FR-07-07 |
| Doubt entry deletion | AI Doubt | 🟢 Low | Doubt history | FR-07-08 |
| AI error handling & rate limiting | AI Doubt | 🟡 Medium | Gemini integration layer | FR-07-09, NFR-SEC-10 |
| AI Concept Explainer UI + query flow | AI Explainer | 🟡 Medium | Gemini integration layer | FR-08-01 to FR-08-04 |
| Explanation caching (24-hour) | AI Explainer | 🟡 Medium | AI Concept Explainer | FR-08-05 |

---

## 6. Analytics & Intelligence Features

*Data Science / ML components of the tech stack.*

| Feature | Module | Complexity | Depends On | Linked FR |
|---|---|---|---|---|
| Performance data aggregation pipeline | Analytics | 🟡 Medium | Practice engine, Mock Test | FR-09-01 to FR-09-05 |
| Dashboard summary cards | Dashboard | 🟢 Low | Aggregation pipeline | FR-02-02 to FR-02-05 |
| Subject-wise performance chart (Chart.js) | Dashboard | 🟡 Medium | Aggregation pipeline | FR-02-06 |
| Full analytics page (trend, radar, breakdown charts) | Analytics | 🔴 High | Aggregation pipeline | FR-09-01 to FR-09-08 |
| Analytics filtering (subject, date range) | Analytics | 🟡 Medium | Full analytics page | FR-09-07 |
| ML model training script (offline, Scikit-Learn) | ML Pipeline | 🔴 High | Sufficient practice data | FR-10-01, FR-10-06 |
| ML model serialization (Joblib) | ML Pipeline | 🟢 Low | ML training script | FR-10-06 |
| Weak area inference service | ML Pipeline | 🔴 High | Serialized model | FR-10-02, FR-10-03 |
| Rule-based fallback classification | ML Pipeline | 🟢 Low | Weak area inference service | FR-10-07 |
| Weak topics widget (dashboard + syllabus) | Dashboard | 🟡 Medium | Weak area inference service | FR-02-07, FR-03-07 |

---

## 7. Engagement Features

*Lower-complexity features that increase platform "stickiness."*

| Feature | Module | Complexity | Depends On | Linked FR |
|---|---|---|---|---|
| Study planner (create/edit plan) | Planner | 🟡 Medium | Syllabus structure | FR-11-01, FR-11-05 |
| Study planner calendar view | Planner | 🟡 Medium | Study planner | FR-11-02 |
| Auto-completion of planned topics | Planner | 🟢 Low | Study planner, Practice engine | FR-11-03 |
| Leaderboard ranking calculation | Leaderboard | 🟡 Medium | Aggregation pipeline | FR-14-01 |
| Leaderboard UI + subject filter | Leaderboard | 🟢 Low | Ranking calculation | FR-14-02 to FR-14-05 |
| Milestone detection (streaks, counts) | Notifications | 🟡 Medium | Aggregation pipeline | FR-13-01 |
| In-app notification UI + unread count | Notifications | 🟢 Low | Milestone detection | FR-13-03, FR-13-04 |
| Streak counter on dashboard | Dashboard | 🟢 Low | Aggregation pipeline | FR-02-10 |

---

## 8. Administration Features

| Feature | Module | Complexity | Depends On | Linked FR |
|---|---|---|---|---|
| Django admin extension for content models | Admin | 🟢 Low | Content models | FR-12-03, FR-12-07 |
| Bulk CSV question upload + validation | Admin | 🟡 Medium | Question Bank model | FR-04-06, FR-12-04 |
| Student account management (search, activate/deactivate) | Admin | 🟢 Low | Auth module | FR-12-02 |
| Question report review interface | Admin | 🟡 Medium | Question reporting (student side) | FR-12-06 |
| Platform usage statistics view | Admin | 🟡 Medium | Aggregation pipeline | FR-12-05 |

---

## 9. Dependency Graph

This simplified graph shows the critical build order at the module level:

```
┌─────────────┐
│    Auth     │  (Foundation — Week 1)
└──────┬──────┘
       │
       ▼
┌─────────────┐     ┌──────────────┐
│  Content     │────▶│  Question    │  (Foundation — Week 1)
│  Structure   │     │  Bank        │
└──────┬──────┘     └──────┬───────┘
       │                    │
       ▼                    ▼
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│  Practice    │     │  Mock Test   │     │  Gemini AI   │  (Core — Week 2)
│  Engine      │     │  Module      │     │  Integration │
└──────┬──────┘     └──────┬───────┘     └──────┬───────┘
       │                    │                     │
       └────────┬───────────┘                     ├──────────┐
                 ▼                                 ▼          ▼
        ┌─────────────────┐              ┌──────────────┐ ┌──────────────┐
        │  Aggregation     │              │ Doubt Solver │ │  Concept     │
        │  Pipeline        │              │              │ │  Explainer   │
        └────────┬────────┘              └──────────────┘ └──────────────┘
                  │                          (Core — Week 2-3)
                  ▼
   ┌──────────────┬───────────────┬───────────────┐
   ▼              ▼               ▼               ▼
Dashboard    Analytics Page   ML Weak Area    Leaderboard/
                              Detection       Notifications
   (Integration — Week 3)                    (Polish — Week 4)
                  │
                  ▼
          Study Planner
          (Polish — Week 4)
```

---

## 10. Suggested Build Order (4-Week Plan)

This maps directly to the dependency graph above and the story-point budget from Document 05.

| Week | Focus | Key Features Delivered |
|---|---|---|
| **Week 1** | Foundation | Auth, Content Structure (Subjects/Chapters/Topics), Question Bank model + Admin CRUD, Base UI/Design System |
| **Week 2** | Core Learning + AI Integration | Practice Engine, Mock Test Module, Gemini API Integration Layer, Doubt Solver, Concept Explainer |
| **Week 3** | Intelligence Layer | Aggregation Pipeline, Dashboard, Full Analytics, ML Model Training + Weak Area Detection, Adaptive Difficulty |
| **Week 4** | Engagement + Polish + Deployment | Study Planner, Leaderboard, Notifications, Bug Fixes, UI Polish, Deployment to Render/Neon/Cloudinary, Final Testing |

**Why this order?** It follows the dependency graph strictly — you cannot build a meaningful Dashboard (Week 3) before you have practice/test data flowing into it (Week 2), and you cannot demonstrate Adaptive Difficulty (Week 2-3) before the Practice Engine exists (Week 2). This ordering also front-loads risk: the highest-complexity, highest-uncertainty features (Gemini integration, ML model, timed mock test engine) are tackled in Weeks 2-3, leaving Week 4 for polish and deployment rather than scrambling to build core features under deadline pressure.

---

## Document Control

| Field | Value |
|---|---|
| Document ID | CC-FEAT-08 |
| Version | 1.0 |
| Created | 2026-07-29 |
| Last Updated | 2026-07-29 |
| Status | Draft |
| Depends On | CC-FRD-01, CC-US-05, CC-SCOPE-07 |
| Storage Location | `docs/requirements/08_feature_list.md` |

---

*End of Document — ConceptCode Feature List v1.0*
