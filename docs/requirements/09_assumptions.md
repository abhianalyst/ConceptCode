# ConceptCode – AI Powered Adaptive Learning Platform
## Document 09: Assumptions
**Version:** 1.0
**Phase:** Phase 0 – Requirement Analysis
**Status:** Draft – Pending Review
**Prepared By:** Development Team
**Date:** 2026-07-29

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Team & Process Assumptions](#2-team--process-assumptions)
3. [Technical Assumptions](#3-technical-assumptions)
4. [Third-Party Service Assumptions](#4-third-party-service-assumptions)
5. [Data & Content Assumptions](#5-data--content-assumptions)
6. [User Behavior Assumptions](#6-user-behavior-assumptions)
7. [Academic/Evaluation Assumptions](#7-academicevaluation-assumptions)
8. [Assumption Validation Plan](#8-assumption-validation-plan)

---

## 1. Introduction

### 1.1 Purpose
This document records every assumption underlying ConceptCode v1.0's scope, timeline, architecture, and design decisions made in Documents 01–08.

### 1.2 Format
Each assumption is tagged with an **impact level** — what happens to the project if the assumption turns out to be false:

| Impact | Meaning |
|---|---|
| 🔴 Critical | Project scope/timeline must be significantly revised if false |
| 🟡 Moderate | A specific feature/module must be redesigned if false |
| 🟢 Minor | Easily adjusted without major rework if false |

---

## 2. Team & Process Assumptions

| ID | Assumption | Impact |
|---|---|---|
| AS-01 | Both developers are available to dedicate meaningful daily hours (assumed ~4-6 hrs/day) to the project for the full 1-month duration | 🔴 Critical |
| AS-02 | Both developers have working proficiency in Python, Django, and basic frontend (HTML/CSS/Bootstrap/JS) at project start — this project is not also serving as a "learn Django from zero" exercise | 🔴 Critical |
| AS-03 | Task division between the two developers will roughly follow module boundaries (e.g., one developer leans backend/ML, the other leans frontend/AI integration), avoiding constant merge conflicts | 🟡 Moderate |
| AS-04 | No major team availability disruptions (illness, exams, other coursework conflicts) will consume more than a few days total during the 1-month window | 🟡 Moderate |
| AS-05 | The Project Guide/Mentor will be available for at least weekly check-ins to unblock decisions | 🟢 Minor |

---

## 3. Technical Assumptions

| ID | Assumption | Impact |
|---|---|---|
| AS-06 | SQLite is sufficient for local development without needing to replicate PostgreSQL-specific behavior during coding (only final deployment testing needs Neon PostgreSQL) | 🟡 Moderate |
| AS-07 | Django REST Framework is only needed for endpoints requiring AJAX/JS interaction (e.g., practice question submission, AI queries) — most pages will be server-rendered Django templates, not a full SPA | 🟡 Moderate |
| AS-08 | Render's free/hobby tier provides sufficient compute for the MVP's expected traffic (see NFR-SCALE-01: 100 concurrent users) without requiring a paid tier during development/evaluation | 🔴 Critical |
| AS-09 | Render's free-tier "cold start" delay (service sleeping after inactivity) is an acceptable trade-off for a student project and will be clearly understood by evaluators, not mistaken for a performance defect | 🟡 Moderate |
| AS-10 | Chart.js is sufficient for all required visualizations (line, bar, radar) without needing a heavier charting library | 🟢 Minor |
| AS-11 | Cloudinary's free tier storage/bandwidth quota is sufficient for MVP-scale image uploads (profile pictures, limited question images) | 🟡 Moderate |
| AS-12 | The development team has stable internet access sufficient for API-dependent development and testing (Gemini calls, deployment) | 🟡 Moderate |

---

## 4. Third-Party Service Assumptions

| ID | Assumption | Impact |
|---|---|---|
| AS-13 | The Google Gemini API's free/low-cost tier provides sufficient request quota to support development, testing, and evaluation-period usage without incurring significant cost | 🔴 Critical |
| AS-14 | The Gemini API's response quality for NEET-level Physics/Chemistry/Biology content is sufficiently accurate to be presented to students without a manual expert-review pipeline in v1.0 (acknowledging this is a known limitation, not a guarantee of AI correctness) | 🔴 Critical |
| AS-15 | Gemini API's terms of service permit the intended use case (educational AI tutoring for a student-built platform) without requiring enterprise agreements | 🟡 Moderate |
| AS-16 | Neon PostgreSQL's free tier connection and storage limits are sufficient for MVP data volume (student records, question bank, attempt history) | 🟡 Moderate |
| AS-17 | None of the third-party services (Render, Neon, Cloudinary, Gemini) will undergo breaking API/pricing changes during the 1-month development window | 🟢 Minor |

---

## 5. Data & Content Assumptions

| ID | Assumption | Impact |
|---|---|---|
| AS-18 | A representative question bank (500-1000 questions across 3-5 chapters per subject, per Document 07 Section 7) is achievable to source/curate within the timeline, separate from development effort | 🔴 Critical |
| AS-19 | Questions can be legally sourced/created without copyright infringement (i.e., original questions or questions from sources explicitly permitting educational reuse, not copied verbatim from copyrighted question banks) | 🔴 Critical |
| AS-20 | Sufficient synthetic or early-user practice data can be generated or collected to meaningfully train and validate the ML weak-area detection model before final evaluation | 🟡 Moderate |
| AS-21 | The NCERT-based NEET syllabus structure used for Subject/Chapter/Topic hierarchy remains stable and doesn't require restructuring mid-project | 🟢 Minor |

---

## 6. User Behavior Assumptions

| ID | Assumption | Impact |
|---|---|---|
| AS-22 | Real or simulated student users will generate enough practice/test attempts (minimum threshold, see UC-04 Alternate Flow A1) for weak-area detection to produce meaningful results during evaluation/demo | 🟡 Moderate |
| AS-23 | Students primarily access the platform via mobile browsers (per personas Ananya, Rohan), validating the mobile-first responsive priority | 🟢 Minor |
| AS-24 | Students will use the AI Doubt Solver responsibly (asking genuine academic questions) — the system prompt guardrail (FR-07-10) is assumed sufficient without needing heavy moderation tooling in v1.0 | 🟡 Moderate |

---

## 7. Academic/Evaluation Assumptions

| ID | Assumption | Impact |
|---|---|---|
| AS-25 | The evaluation panel/project guide will assess the project based on both documentation (this Phase 0 process) and the working product — not solely on feature count | 🟡 Moderate |
| AS-26 | A live/deployed demo (Render) will be accessible during evaluation, rather than requiring only local demonstration | 🟡 Moderate |
| AS-27 | The 1-month timeline is fixed and non-negotiable, making the Project Scope document (Document 07) an accurate reflection of what must be achieved | 🔴 Critical |

---

## 8. Assumption Validation Plan

Not all assumptions can be verified before coding begins — but the highest-impact (🔴 Critical) ones should be checked as early as possible, ideally in Week 1, to avoid discovering a broken foundation late.

| Assumption | Validation Action | When |
|---|---|---|
| AS-08 (Render capacity) | Deploy a minimal "Hello World" Django app early to confirm hosting works as expected | Week 1 |
| AS-13 (Gemini quota/cost) | Review current Gemini API pricing/free-tier documentation directly; run a small batch of test queries and monitor usage | Week 1 |
| AS-14 (AI answer quality) | Manually test Gemini responses against 10-15 known NEET questions to sanity-check accuracy before building the full UI around it | Week 1-2 |
| AS-18/AS-19 (Question bank sourcing) | Begin sourcing/curating questions in parallel with Week 1 development, not after | Week 1 (parallel) |
| AS-20/AS-22 (Data for ML) | Decide early whether to seed the database with synthetic practice data to guarantee the ML demo works regardless of real usage | Week 2-3 |
| AS-02 (Team proficiency) | Honest team self-assessment before Week 1 begins; flag any skill gaps immediately so learning time is budgeted in, not hidden | Before Week 1 |

**Why validate 🔴 Critical assumptions in Week 1 specifically?** If, for example, AS-13 (Gemini quota) turns out to be wrong — the free tier is too restrictive — you need to know that in Week 1, when you can still adjust caching strategy (FR-08-05), rate limits (NFR-SEC-10), or even request an alternative approach, not in Week 4 when the AI features are already built around a false assumption.

---

## Document Control

| Field | Value |
|---|---|
| Document ID | CC-ASM-09 |
| Version | 1.0 |
| Created | 2026-07-29 |
| Last Updated | 2026-07-29 |
| Status | Draft |
| Depends On | CC-FEAT-08, CC-SCOPE-07 |
| Storage Location | `docs/requirements/09_assumptions.md` |
| Feeds Into | Document 11: Risk Analysis |

---

*End of Document — ConceptCode Assumptions v1.0*
