# ConceptCode – AI Powered Adaptive Learning Platform
## Document 10: Constraints
**Version:** 1.0
**Phase:** Phase 0 – Requirement Analysis
**Status:** Draft – Pending Review
**Prepared By:** Development Team
**Date:** 2026-07-29

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Time Constraints](#2-time-constraints)
3. [Resource Constraints](#3-resource-constraints)
4. [Technology Constraints](#4-technology-constraints)
5. [Budget Constraints](#5-budget-constraints)
6. [Regulatory & Policy Constraints](#6-regulatory--policy-constraints)
7. [Design Constraints](#7-design-constraints)
8. [Constraint-to-Decision Traceability](#8-constraint-to-decision-traceability)

---

## 1. Introduction

### 1.1 Purpose
This document records every fixed, non-negotiable limitation governing ConceptCode v1.0's development, and explains how each constraint has already shaped decisions made in Documents 01–09.

### 1.2 Relationship to Assumptions
Where Document 09 listed things we *believe* to be true (and plan to validate), this document lists things that are *simply given* — imposed by the project brief, team size, timeline, or external providers, and not subject to change through effort or validation.

---

## 2. Time Constraints

| ID | Constraint | Design Impact |
|---|---|---|
| CON-T-01 | The entire project — from Requirement Analysis through deployment — must be completed within **1 calendar month** | Directly drove the MVP scoping in Document 07 and the 4-week build plan in Document 08 |
| CON-T-02 | The team consists of exactly **2 developers**, with no ability to add team members mid-project | Drove decisions to reuse existing tools (Django admin, DRF) over building custom infrastructure |
| CON-T-03 | Some portion of each developer's daily time is likely shared with other academic coursework/exams (unstated but realistic for a Final Year Project context) | Reinforces the need for tight scope discipline (Document 07) and a clear change-control process |

---

## 3. Resource Constraints

| ID | Constraint | Design Impact |
|---|---|---|
| CON-R-01 | No dedicated QA/testing team — the 2 developers are also the testers | Testing strategy (Phase 5) must be lightweight and largely automatable (unit tests, not manual QA teams) |
| CON-R-02 | No dedicated DevOps engineer — deployment must use managed platforms (Render, Neon, Cloudinary) rather than self-managed infrastructure | Justifies the choice of PaaS providers over, e.g., self-hosted Docker/Kubernetes |
| CON-R-03 | No professional content/subject-matter expert on the team to author NEET questions from scratch at scale | Justifies Document 07's decision to limit question bank scope to a representative subset, sourced carefully (see AS-19) |
| CON-R-04 | No dedicated UI/UX designer — one or both developers must also perform design work | Justifies adopting a fixed, pre-decided design system (color palette, Poppins typography, Bootstrap) rather than an open-ended design exploration phase |

---

## 4. Technology Constraints

These are **mandated by the project brief itself** and are the least negotiable of all constraints.

| ID | Constraint | Design Impact |
|---|---|---|
| CON-TECH-01 | Backend must use **Python, Django, and Django REST Framework** | All server-side architecture decisions are Django-idiomatic (apps-based modular structure, Django ORM, DRF serializers/viewsets for AJAX endpoints) |
| CON-TECH-02 | Frontend must use **HTML5, CSS3, Bootstrap 5.3.8, JavaScript, and Chart.js** — no other CSS/JS frameworks (e.g., React, Vue, Tailwind) | UI is server-rendered Django templates with Bootstrap components; no SPA architecture |
| CON-TECH-03 | Development database must be **SQLite**; production database must be **Neon PostgreSQL** | Requires Django-ORM-only queries (no raw SQL) to remain database-portable (see NFR-PORT-02) |
| CON-TECH-04 | Deployment must use **Render** (application hosting) and **Cloudinary** (media storage) | Drives environment variable management strategy and static/media file serving configuration specific to these platforms |
| CON-TECH-05 | AI features must use the **Google Gemini API** specifically — no substituting OpenAI, Anthropic, or other LLM providers | All AI integration code is written directly against Gemini's API contract |
| CON-TECH-06 | Machine Learning must use **NumPy, Pandas, Scikit-Learn, and Joblib** — no deep learning frameworks (TensorFlow, PyTorch) | Constrains the weak-area detection and adaptive difficulty models to classical ML approaches (e.g., logistic regression, decision trees, random forests) rather than neural networks — which is appropriate given the tabular, moderate-volume nature of the performance data anyway |
| CON-TECH-07 | Version control must use **Git and GitHub** | Standard practice; drives the branching/commit conventions in NFR-MAINT-06 |

**Why is CON-TECH-06 actually a good constraint, not just a limitation?** It's worth noting explicitly: classical ML (Scikit-Learn) is the *correct* technical choice for this problem even without the constraint. Weak-area detection and adaptive difficulty are tabular classification/regression problems on a modest dataset (per-student, per-topic performance metrics) — exactly the kind of problem Scikit-Learn excels at, and where deep learning would be unnecessary complexity. This constraint aligns with, rather than fights against, good engineering judgment.

---

## 5. Budget Constraints

| ID | Constraint | Design Impact |
|---|---|---|
| CON-B-01 | This is a self-funded student project with **no operational budget** for paid infrastructure | Every service (Render, Neon, Cloudinary, Gemini API) must operate within free or near-free tiers for the MVP/evaluation period |
| CON-B-02 | No budget for licensed/paid question bank content | Question sourcing must rely on original authorship or explicitly reusable educational sources |
| CON-B-03 | No budget for paid design assets (premium fonts, icon packs, stock photography) beyond free resources (e.g., Google Fonts for Poppins, free icon libraries) | UI must be built entirely from free/open assets |

---

## 6. Regulatory & Policy Constraints

| ID | Constraint | Design Impact |
|---|---|---|
| CON-P-01 | Google Gemini API usage is governed by **Google's API Terms of Service and Acceptable Use Policy**, which the platform cannot violate | System prompts (FR-07-10) must keep the AI within permitted educational use; content moderation guardrails are a policy requirement, not just a UX nicety |
| CON-P-02 | Student data collection is subject to **India's Digital Personal Data Protection Act (DPDP), 2023** principles | Drove NFR-LEGAL-01 and NFR-LEGAL-02 (privacy policy, consent, data minimization) |
| CON-P-03 | NEET question content sourcing must respect copyright law — previous years' official NEET papers are generally in the public domain / releasable by NTA, but third-party coaching material is not | Drove AS-19 and the content-sourcing caution in Document 07 |
| CON-P-04 | The project must comply with the academic institution's Final Year Project submission guidelines and evaluation rubric (format, documentation requirements, plagiarism policy) | This entire Phase 0 documentation process is partly structured to satisfy this constraint, alongside genuine engineering value |

---

## 7. Design Constraints

| ID | Constraint | Design Impact |
|---|---|---|
| CON-D-01 | UI must use the fixed color palette: background `#E2ECF9`, cards `#FFFFFF`, primary accent `#1A1D24` | No open design exploration on color; all UI components are built against this fixed palette |
| CON-D-02 | Typography must use **Poppins** exclusively | Drives font import strategy (Google Fonts CDN) and typographic scale decisions in Phase 2 (Design) |
| CON-D-03 | The interface must read as a "premium SaaS dashboard" — minimal, professional, responsive, modern, consistent | This qualitative constraint governs component density, whitespace usage, and visual hierarchy decisions to be made in the UI/UX design phase |
| CON-D-04 | Bootstrap must be the primary CSS framework | No custom CSS grid system or utility framework (e.g., Tailwind) may replace Bootstrap's grid/components, though custom CSS may supplement it for the specific design system above |

---

## 8. Constraint-to-Decision Traceability

This table makes explicit which prior decisions (from Documents 01–09) exist *because of* a specific constraint — useful evidence for your evaluator that architecture choices are deliberate.

| Prior Decision | Governing Constraint(s) |
|---|---|
| No Teacher role in v1.0 (Document 07) | CON-T-01, CON-T-02 (time, team size) |
| Server-rendered Django templates over SPA (Document 08) | CON-TECH-02 (mandated frontend stack) |
| Django ORM only, no raw SQL (NFR-PORT-02) | CON-TECH-03 (dual SQLite/PostgreSQL requirement) |
| Classical ML (Scikit-Learn) for weak-area detection (Document 08) | CON-TECH-06 (mandated ML stack) |
| Representative (not exhaustive) question bank (Document 07) | CON-R-03, CON-B-02 (no content expert, no content budget) |
| Rate limiting on AI requests (NFR-SEC-10) | CON-B-01, CON-P-01 (budget, Gemini ToS) |
| Fixed color palette and typography (Phase 2, upcoming) | CON-D-01, CON-D-02 |
| Extending Django admin instead of custom admin UI (Document 08) | CON-T-01, CON-R-04 (time, no dedicated designer) |

---

## Document Control

| Field | Value |
|---|---|
| Document ID | CC-CONST-10 |
| Version | 1.0 |
| Created | 2026-07-29 |
| Last Updated | 2026-07-29 |
| Status | Draft |
| Depends On | CC-SCOPE-07, CC-FEAT-08, CC-ASM-09 |
| Storage Location | `docs/requirements/10_constraints.md` |
| Feeds Into | Document 11: Risk Analysis |

---

*End of Document — ConceptCode Constraints v1.0*
