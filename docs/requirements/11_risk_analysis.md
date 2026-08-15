# ConceptCode – AI Powered Adaptive Learning Platform
## Document 11: Risk Analysis
**Version:** 1.0
**Phase:** Phase 0 – Requirement Analysis
**Status:** Draft – Pending Review
**Prepared By:** Development Team
**Date:** 2026-07-29

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Risk Scoring Methodology](#2-risk-scoring-methodology)
3. [Technical Risks](#3-technical-risks)
4. [Timeline & Resource Risks](#4-timeline--resource-risks)
5. [Third-Party Dependency Risks](#5-third-party-dependency-risks)
6. [Data & Content Risks](#6-data--content-risks)
7. [Security & Compliance Risks](#7-security--compliance-risks)
8. [Risk Heat Map](#8-risk-heat-map)
9. [Top 5 Risks Requiring Immediate Attention](#9-top-5-risks-requiring-immediate-attention)

---

## 1. Introduction

### 1.1 Purpose
This document catalogs risks to ConceptCode v1.0's successful delivery, scores them, and defines mitigation and contingency plans for each — built directly on the 🔴 Critical items flagged in Document 09 (Assumptions) and Document 10 (Constraints).

### 1.2 Risk vs. Assumption vs. Constraint
To keep these three related documents distinct:

| Document | Question Answered |
|---|---|
| Assumptions (09) | "What are we taking for granted?" |
| Constraints (10) | "What can we not change?" |
| **Risk Analysis (11)** | **"What could go wrong, how badly, and what do we do about it?"** |

A risk is often what happens when an assumption turns out false, or when a constraint proves harder to work within than expected.

---

## 2. Risk Scoring Methodology

Each risk is scored on two axes, then multiplied to produce a **Risk Score**:

| Likelihood | Score |
|---|---|
| Low (unlikely to occur) | 1 |
| Medium (plausible) | 2 |
| High (likely to occur) | 3 |

| Impact | Score |
|---|---|
| Low (minor delay/rework) | 1 |
| Medium (feature must be cut/redesigned) | 2 |
| High (threatens overall project delivery) | 3 |

**Risk Score = Likelihood × Impact** (range: 1–9)

| Score Range | Priority |
|---|---|
| 6–9 | 🔴 High Priority |
| 3–4 | 🟡 Medium Priority |
| 1–2 | 🟢 Low Priority |

---

## 3. Technical Risks

| ID | Risk | Likelihood | Impact | Score | Mitigation | Contingency |
|---|---|---|---|---|---|---|
| RISK-T-01 | Adaptive difficulty ML integration (FR-05-03) takes significantly longer than estimated due to real-time inference complexity | Medium (2) | High (3) | 6 🔴 | Build and test the ML inference function in isolation early (Week 2), before wiring it into the practice UI | Fall back to a simpler rule-based adaptive logic (e.g., "2 correct → harder, 2 incorrect → easier") without full ML inference for v1.0, upgrading later |
| RISK-T-02 | Server-authoritative mock test timer (UC-01) has subtle bugs around timezone handling, auto-submission edge cases, or clock drift | Medium (2) | High (3) | 6 🔴 | Write dedicated unit tests for timer logic early; test with artificially short mock tests (e.g., 2-minute test) to quickly validate auto-submit behavior | If bugs persist near deadline, simplify to a client-side timer with server-side validation only at submission (less robust but functional) |
| RISK-T-03 | N+1 query problems or unoptimized queries cause dashboard/analytics pages to be slow (violating NFR-PERF-01, NFR-PERF-06) | Medium (2) | Medium (2) | 4 🟡 | Use Django Debug Toolbar from Week 1 onward, not just before deployment, to catch query issues early | Add database indexes and `select_related`/`prefetch_related` reactively if performance issues surface late |
| RISK-T-04 | Deployment configuration issues (static files, environment variables, database migrations) cause a broken or delayed first production deploy | Medium (2) | Medium (2) | 4 🟡 | Deploy a minimal skeleton app to Render in Week 1 (see AS-08 validation plan) to surface configuration issues early, not in Week 4 | Reserve 2 buffer days before final deadline explicitly for deployment troubleshooting |

---

## 4. Timeline & Resource Risks

| ID | Risk | Likelihood | Impact | Score | Mitigation | Contingency |
|---|---|---|---|---|---|---|
| RISK-R-01 | One or both developers lose several days to illness, exams, or other coursework during the 1-month window | Medium (2) | High (3) | 6 🔴 | Build a small time buffer into the plan (treat Week 4 partially as slack, not fully feature-loaded); maintain daily async check-ins to detect slippage early | Trigger the Change Control Process (Document 07, Section 8) to cut Medium/Low priority features (Study Planner, Notifications, Leaderboard) per the prioritization in Document 05 |
| RISK-R-02 | Feature estimates (story points, Document 05) prove optimistic, and Week 3-4 features slip | High (3) | High (3) | 9 🔴 | Track actual time spent per feature against story-point estimates starting Week 1; recalibrate weekly | Fall back to the Document 07 in-scope/out-of-scope boundary immediately — cut Low priority features first (Notifications, Leaderboard), then Medium (Study Planner) |
| RISK-R-03 | Merge conflicts or integration issues between the two developers' work slow down progress | Medium (2) | Medium (2) | 4 🟡 | Enforce module-based task division (per Document 08's dependency graph) so developers rarely touch the same files; use feature branches with frequent, small commits | Schedule brief daily syncs specifically to catch integration issues before they compound |
| RISK-R-04 | Team underestimates the learning curve for a specific technology (e.g., Chart.js customization, DRF serializers, Gemini API specifics) | Medium (2) | Medium (2) | 4 🟡 | Time-box exploratory learning to short spikes (e.g., half a day) at the start of each new feature area, rather than open-ended learning | If a technology proves too time-consuming, simplify the implementation (e.g., simpler chart types) rather than abandoning the feature |

---

## 5. Third-Party Dependency Risks

| ID | Risk | Likelihood | Impact | Score | Mitigation | Contingency |
|---|---|---|---|---|---|---|
| RISK-D-01 | Google Gemini API free-tier quota is insufficient for development, testing, and demo-day usage combined (relates to AS-13) | Medium (2) | High (3) | 6 🔴 | Validate actual quota limits in Week 1 (Document 09, Section 8); implement caching (FR-08-05) and rate limiting (NFR-SEC-10) from the start, not as an afterthought | If quota is exhausted near evaluation, pre-generate and cache a demo dataset of AI responses to guarantee a working demo regardless of live API status |
| RISK-D-02 | Gemini API response quality for NEET-level science content is inconsistent or occasionally incorrect (relates to AS-14) | Medium (2) | Medium (2) | 4 🟡 | Test the API against a curated set of known-answer NEET questions before building the full feature around it; keep AI responses clearly labeled "AI-generated" (NFR-AI-04) to set correct user expectations | Add a lightweight "Report this answer" mechanism so quality issues are visible and can inform future prompt tuning |
| RISK-D-03 | Render free-tier cold starts create a poor first impression during live evaluation (relates to AS-09) | High (3) | Medium (2) | 6 🔴 | "Warm up" the deployed app a few minutes before any scheduled demo/evaluation by visiting it manually | Clearly explain the free-tier cold-start behavior to evaluators proactively, framing it as a documented, understood trade-off (Document 10, CON-B-01) rather than a hidden flaw |
| RISK-D-04 | Neon PostgreSQL free-tier connection limits are hit under concurrent load during evaluation/demo | Low (1) | Medium (2) | 2 🟢 | Configure Django's database connection pooling appropriately (NFR-SCALE-04); avoid opening unnecessary long-lived connections | Reduce concurrent test load during live evaluation if this becomes an issue |

---

## 6. Data & Content Risks

| ID | Risk | Likelihood | Impact | Score | Mitigation | Contingency |
|---|---|---|---|---|---|---|
| RISK-C-01 | Sourcing/curating a legally clean, sufficiently large question bank (500-1000 questions) takes longer than expected, delaying feature testing (relates to AS-18, AS-19) | High (3) | High (3) | 9 🔴 | Begin question sourcing in Week 1, in parallel with development (not sequentially after); prioritize a small working set (e.g., 100-150 questions across a few chapters) to unblock feature development immediately, then expand in parallel | If the full question bank isn't ready by Week 3, proceed with the smaller working set for the final demo — quality and correctness of features matters more than question bank size |
| RISK-C-02 | Insufficient real/simulated practice data exists to make the ML weak-area detection model produce meaningful, convincing output for evaluation (relates to AS-20, AS-22) | Medium (2) | High (3) | 6 🔴 | Generate a realistic synthetic dataset (varying accuracy patterns across simulated students) specifically to train and validate the ML model early, independent of real usage | If real usage data is thin by evaluation time, clearly present the model's training methodology using synthetic + limited real data as a valid, disclosed approach — common practice in early-stage ML products |
| RISK-C-03 | A question in the bank is later found to be factually incorrect or ambiguous after being used in mock tests | Medium (2) | Low (1) | 2 🟢 | Implement the question reporting feature (FR-05-07, FR-12-06) early enough for the admin to catch and fix issues before evaluation | Admin manually reviews and corrects/deactivates flagged questions |

---

## 7. Security & Compliance Risks

| ID | Risk | Likelihood | Impact | Score | Mitigation | Contingency |
|---|---|---|---|---|---|---|
| RISK-S-01 | API keys (Gemini, Cloudinary, database credentials) are accidentally committed to the public GitHub repository | Medium (2) | High (3) | 6 🔴 | Set up `.gitignore` for `.env` files from the very first commit (Week 1, Day 1); use a pre-commit hook or manual checklist before every push to scan for accidental secrets | If a secret is leaked, immediately revoke/rotate the exposed key and force-push a cleaned history (or use tools like `git filter-repo`) |
| RISK-S-02 | A student submits abusive, harmful, or policy-violating content to the AI Doubt Solver, and the response reflects poorly on the platform | Low (1) | Medium (2) | 2 🟢 | Rely on the Gemini API's own content safety filtering plus a scoped system prompt (FR-07-10) restricting the assistant to academic topics | Log flagged/unusual queries for manual review; add a report mechanism if this becomes a recurring issue |
| RISK-S-03 | Insufficient input validation on forms (registration, CSV upload, question bank admin) allows malformed or malicious data into the system | Low (1) | Medium (2) | 2 🟢 | Use Django's built-in form/model validation consistently; validate CSV uploads row-by-row with clear error reporting (UC-12) | Fix and redeploy promptly if a validation gap is discovered; Django's ORM inherently protects against SQL injection |

---

## 8. Risk Heat Map

```
                         IMPACT
              Low(1)      Medium(2)      High(3)
          ┌───────────┬─────────────┬─────────────┐
   High(3)│           │             │ RISK-R-02 🔴 │
          │           │             │ RISK-C-01 🔴 │
          ├───────────┼─────────────┼─────────────┤
LIKELIHOOD│           │ RISK-D-03 🔴│ RISK-T-01 🔴 │
  Medium  │           │             │ RISK-T-02 🔴 │
   (2)    │ RISK-C-03 │ RISK-T-03 🟡│ RISK-R-01 🔴 │
          │    🟢     │ RISK-T-04 🟡│ RISK-D-01 🔴 │
          │           │ RISK-R-03 🟡│ RISK-C-02 🔴 │
          │           │ RISK-R-04 🟡│ RISK-S-01 🔴 │
          │           │ RISK-D-02 🟡│              │
          ├───────────┼─────────────┼─────────────┤
   Low(1) │           │ RISK-S-02 🟢│              │
          │           │ RISK-S-03 🟢│              │
          │           │ RISK-D-04 🟢│              │
          └───────────┴─────────────┴─────────────┘
```

---

## 9. Top 5 Risks Requiring Immediate Attention

Ranked by Risk Score, these are the risks that should influence Week 1 planning directly — not deferred for "later":

| Rank | Risk | Score | Immediate Action (Week 1) |
|---|---|---|---|
| 1 | RISK-R-02: Feature estimates prove optimistic | 9 | Track actual vs. estimated time from Day 1; set a Week-2 checkpoint to recalibrate scope if needed |
| 1 (tied) | RISK-C-01: Question bank sourcing takes too long | 9 | Start sourcing questions in Week 1, in parallel with coding, targeting a small working set first |
| 3 | RISK-T-01: Adaptive ML integration complexity | 6 | Build and test the ML inference function in isolation before UI integration |
| 3 (tied) | RISK-T-02: Mock test timer edge cases | 6 | Write timer unit tests early; test with short artificial test durations |
| 3 (tied) | RISK-R-01: Team availability disruption | 6 | Build slack into Week 4; maintain daily async check-ins |
| 3 (tied) | RISK-D-01: Gemini API quota insufficiency | 6 | Validate real quota limits in Week 1; implement caching/rate-limiting from the start, not retroactively |
| 3 (tied) | RISK-D-03: Render cold starts hurt demo impression | 6 | Plan to "warm up" the app before any live evaluation; document this trade-off proactively |
| 3 (tied) | RISK-C-02: Insufficient data for ML model | 6 | Generate synthetic training data early, independent of real usage patterns |
| 3 (tied) | RISK-S-01: Accidental API key leak to GitHub | 6 | Set up `.gitignore` and secret-scanning discipline from the very first commit |

**Why present this as a ranked "Week 1 action list" rather than just a scored table?** A risk register that just sits in a document provides little value. Converting the top risks into concrete Week 1 actions is what makes this document operational — it should directly shape your first week's task list, not just exist as an academic artifact.

---

## Document Control

| Field | Value |
|---|---|
| Document ID | CC-RISK-11 |
| Version | 1.0 |
| Created | 2026-07-29 |
| Last Updated | 2026-07-29 |
| Status | Draft |
| Depends On | CC-ASM-09, CC-CONST-10 |
| Storage Location | `docs/requirements/11_risk_analysis.md` |

---

*End of Document — ConceptCode Risk Analysis v1.0*
