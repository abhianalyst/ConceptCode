# ConceptCode – AI Powered Adaptive Learning Platform
## Document 07: Project Scope
**Version:** 1.0
**Phase:** Phase 0 – Requirement Analysis
**Status:** Draft – Pending Review
**Prepared By:** Development Team
**Date:** 2026-07-29

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Project Objective](#2-project-objective)
3. [In-Scope Features (v1.0 MVP)](#3-in-scope-features-v10-mvp)
4. [Out-of-Scope Features (Deferred to v2.0+)](#4-out-of-scope-features-deferred-to-v20)
5. [Scope Boundary Rationale](#5-scope-boundary-rationale)
6. [Geographic and Language Scope](#6-geographic-and-language-scope)
7. [Timeline-Driven Scope Constraints](#7-timeline-driven-scope-constraints)
8. [Change Control Process](#8-change-control-process)

---

## 1. Introduction

### 1.1 Purpose
This document defines the precise boundary of what will be delivered as ConceptCode v1.0 within the 1-month, 2-developer timeline, and explicitly lists what is deferred to future versions.

### 1.2 Why a Hard Boundary Matters
Every feature discussed in Documents 01–06 is *desirable*. Not every feature is *achievable* in one month by two developers. This document is where desirability is filtered through feasibility.

---

## 2. Project Objective

> Deliver a production-ready, deployed, web-based adaptive learning platform for NEET aspirants that demonstrates: (1) a functioning adaptive practice engine, (2) AI-powered doubt resolution and concept explanation via Google Gemini, (3) ML-based weak area detection, and (4) professional-grade UI/UX — all within a 1-month development cycle by a 2-person team.

This objective statement is the filter every scope decision below is measured against. A feature makes it into v1.0 only if it materially supports this objective within the time and team constraints.

---

## 3. In-Scope Features (v1.0 MVP)

The following modules, drawn directly from Document 01 (Functional Requirements), are **committed for v1.0 delivery**:

| # | Module | Justification for Inclusion |
|---|---|---|
| 1 | Authentication & User Management | Foundational — nothing else works without it |
| 2 | Student Dashboard | Core entry point; demonstrates personalization immediately |
| 3 | Subject/Chapter/Topic Syllabus Structure | Foundational content architecture |
| 4 | Question Bank (with admin CRUD + CSV bulk upload) | Foundational content, required for practice/tests |
| 5 | Adaptive Practice Engine (ML-driven difficulty) | Core differentiator — directly addresses the "AI Powered Adaptive" claim in the project name |
| 6 | Mock Test Module (Full + Subject-wise, NEET marking scheme) | Core value proposition for NEET-specific exam simulation |
| 7 | AI Doubt Solver (Gemini API) | Core differentiator — directly addresses the "AI Powered" claim |
| 8 | AI Concept Explainer (Gemini API) | Core differentiator, reuses the same AI integration pattern as Doubt Solver |
| 9 | Performance Analytics (charts, breakdowns) | Demonstrates data-driven personalization, core to project's academic value (Data Science component) |
| 10 | Weak Area Detection (ML model, Scikit-Learn) | Core differentiator — directly addresses the "Data Scientist" and ML components of the tech stack |
| 11 | Basic Admin Panel (extending Django admin) | Required to operate the platform at all (content management) |
| 12 | Study Planner (basic version) | Medium-effort, high-value for the Rohan persona; kept but simplified (see Section 5) |
| 13 | Leaderboard (basic version) | Low-effort using existing performance data; strong demo/engagement value |
| 14 | Notifications (in-app only, milestone-based) | Low-effort, reinforces the "polished SaaS product" impression |

---

## 4. Out-of-Scope Features (Deferred to v2.0+)

The following are **explicitly excluded** from v1.0. This is not a rejection of these ideas — it is a deliberate deferral, documented so scope discussions have a clear reference point.

| # | Feature | Reason for Exclusion |
|---|---|---|
| 1 | Teacher/Mentor role and dashboard | Adds a third user role with its own permission model, UI, and workflows — disproportionate effort for a 1-month MVP |
| 2 | Live/synchronous classes or video content | Requires video infrastructure (streaming, storage) entirely outside the current tech stack and timeline |
| 3 | Payment gateway / premium subscriptions | No monetization requirement for an academic MVP; introduces PCI-adjacent compliance concerns not justified at this stage |
| 4 | Native mobile apps (iOS/Android) | The responsive web app (Bootstrap) satisfies mobile usage needs (personas Ananya, Rohan) without the cost of separate native codebases |
| 5 | Peer-to-peer discussion forums / social features | Introduces moderation, spam, and community-management concerns outside current scope |
| 6 | Multi-language support (regional languages) | English-only for v1.0; syllabus content and AI prompts are English-medium NEET material, consistent with most current NEET coaching materials |
| 7 | Offline mode (PWA with full offline sync) | Significant engineering complexity (service workers, conflict resolution) not justified for MVP |
| 8 | Advanced proctoring (webcam monitoring during mock tests) | Requires additional infrastructure and raises privacy/compliance complexity beyond MVP needs |
| 9 | AI-generated question creation (auto-generating new questions via Gemini) | Introduces content-quality-control risk (AI-generated questions must be expert-verified before use); deferred until a review workflow exists |
| 10 | Real-time multiplayer quiz/battle mode | Requires WebSocket infrastructure; a "nice to have" engagement feature, not core to exam preparation |
| 11 | Detailed institutional/coaching-partner integrations (B2B features) | No B2B stakeholder identified for this academic MVP (see Document 03) |
| 12 | Push notifications (email/SMS/browser push) | In-app notifications (in scope) satisfy the core need; external notification channels add infrastructure (Celery + a message service) not justified for MVP |

---

## 5. Scope Boundary Rationale

Some in-scope features are **simplified** rather than fully excluded — a common and effective scope-management technique. This is worth calling out explicitly:

| Feature | Full Vision (Future) | v1.0 Simplified Version |
|---|---|---|
| Study Planner | Auto-generated, AI-optimized daily schedules | Manual topic + date selection, auto-complete on accuracy threshold |
| Leaderboard | Real-time WebSocket updates, weekly/monthly/all-time views | Page-load-refresh ranking, single "overall" + subject filters |
| ML Weak Area Detection | Continuously retrained online-learning model | Batch-retrained model (e.g., weekly), served via Joblib, with rule-based fallback |
| Notifications | Multi-channel (in-app, email, push) | In-app only |
| Admin Panel | Fully custom-built admin UI/UX | Extended Django admin with custom views where necessary |

**Why simplify rather than cut entirely?** Each of these features has real value to at least one persona (Section 4/5 of Document 04). Simplifying preserves that value while respecting the timeline — a better outcome than either cutting the feature completely or over-investing in a "gold-plated" version no one asked for in an MVP.

---

## 6. Geographic and Language Scope

| Dimension | Scope |
|---|---|
| **Geography** | India (NEET is an India-specific exam); no internationalization required |
| **Language** | English only (UI, content, AI prompts/responses) |
| **Curriculum** | NCERT-aligned NEET syllabus (Physics, Chemistry, Biology) as prescribed by the National Testing Agency (NTA) |
| **Currency/Payments** | Not applicable — no payment features in v1.0 (see Section 4) |

---

## 7. Timeline-Driven Scope Constraints

Given the 1-month, 2-developer constraint, scope is further governed by these operating principles:

| Principle | Explanation |
|---|---|
| **MVP over completeness** | Every feature ships in its simplest version that still delivers real value, not its most feature-rich version |
| **Reuse over reinvention** | Django's built-in admin, auth system, and ORM are used and extended rather than replaced with custom equivalents |
| **Core differentiators get priority time** | Adaptive Practice, AI Doubt Solver/Explainer, and Weak Area Detection (the features that justify "AI Powered Adaptive Learning Platform" in the project name) receive the most development time, per the story-point prioritization in Document 05 |
| **Content volume is limited for v1.0** | The question bank does not need to cover the entire NEET syllabus exhaustively at launch — a representative subset (e.g., 3-5 chapters per subject, ~500-1000 questions) is sufficient to demonstrate all functional requirements convincingly |

This last point is worth emphasizing: **populating a complete, syllabus-wide question bank is a content task, not a software engineering task**, and should not consume development time that belongs to building features.

---

## 8. Change Control Process

Even within a fixed scope, requirements evolve. This lightweight process governs any proposed scope change during development:

1. **Proposal:** Either developer documents the proposed addition/change and which section of this document it affects.
2. **Impact Check:** Assess against the story-point budget (Document 05, Section 15) — does adding this require removing something else?
3. **Decision:** Both developers must agree; if it affects timeline risk significantly, consult the Project Guide (SH-05).
4. **Documentation:** Update this Project Scope document and the relevant upstream documents (FR/User Stories) — scope changes are never made silently in code.

**Why this matters even for a 2-person team:** Without this lightweight process, scope changes happen informally in chat messages and get forgotten, leading to half-implemented features. A one-paragraph decision record prevents this.

---

## Document Control

| Field | Value |
|---|---|
| Document ID | CC-SCOPE-07 |
| Version | 1.0 |
| Created | 2026-07-29 |
| Last Updated | 2026-07-29 |
| Status | Draft |
| Depends On | CC-FRD-01, CC-US-05, CC-UC-06 |
| Storage Location | `docs/requirements/07_project_scope.md` |

---

*End of Document — ConceptCode Project Scope v1.0*
