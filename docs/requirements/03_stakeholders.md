# ConceptCode – AI Powered Adaptive Learning Platform
## Document 03: Stakeholders
**Version:** 1.0
**Phase:** Phase 0 – Requirement Analysis
**Status:** Draft – Pending Review
**Prepared By:** Development Team
**Date:** 2026-07-29

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Stakeholder Categories](#2-stakeholder-categories)
3. [Stakeholder Register](#3-stakeholder-register)
4. [Stakeholder Influence–Interest Matrix](#4-stakeholder-influenceinterest-matrix)
5. [Communication & Engagement Plan](#5-communication--engagement-plan)

---

## 1. Introduction

### 1.1 Purpose
This document identifies all individuals, groups, and external systems with a stake in ConceptCode v1.0 — whether they use it, build it, evaluate it, fund it, or impose constraints on it.

### 1.2 Why This Matters for a 2-Developer, 1-Month Project
With a small team and tight timeline, you cannot afford to build features for stakeholders you never identified. This document also protects you academically: your project evaluator will expect to see that you understood the *ecosystem* around your software, not just its code.

---

## 2. Stakeholder Categories

Stakeholders are grouped into four categories, each treated differently in the design process:

| Category | Definition |
|---|---|
| **Primary (Direct Users)** | People who directly interact with the system's UI |
| **Secondary (Indirect/Internal)** | People who influence or govern the project without using it daily |
| **Technical/External Systems** | Third-party platforms and APIs the system depends on |
| **Academic** | Stakeholders relevant specifically because this is a Final Year Project |

---

## 3. Stakeholder Register

### 3.1 Primary Stakeholders (Direct Users)

| ID | Stakeholder | Role/Description | Key Interest | Key Expectation |
|---|---|---|---|---|
| SH-01 | **NEET Aspirant (Student)** | The core end-user; a student preparing for the NEET exam, typically aged 16–19 | Improve exam readiness efficiently | Fast, accurate, personalized, distraction-free practice and feedback |
| SH-02 | **Platform Administrator** | Manages content, users, and platform health | Efficient content and user management | Simple admin tools, visibility into platform usage and issues |

### 3.2 Secondary Stakeholders (Internal/Governance)

| ID | Stakeholder | Role/Description | Key Interest | Key Expectation |
|---|---|---|---|---|
| SH-03 | **Developer 1 (You)** | Full-stack contributor, co-architect | Successful delivery, learning, grading | Clear requirements, maintainable codebase, manageable scope |
| SH-04 | **Developer 2 (Team Partner)** | Full-stack contributor, co-architect | Successful delivery, fair task distribution | Same as above, plus clear module ownership to avoid merge conflicts |
| SH-05 | **Project Guide / Faculty Mentor** | Academic supervisor evaluating the project | Academic rigor, adherence to SE best practices | Proper documentation, evidence of process (not just working code), originality |
| SH-06 | **External Examiner / Evaluation Panel** | Assesses the project during final evaluation | Technical depth, real-world applicability | A working, demonstrable, well-architected product with clear justification of choices |
| SH-07 | **Future Maintainers (v2.0 team)** | Hypothetical future developers extending the platform, including yourselves post-graduation | Codebase clarity, extensibility | Clean modular architecture, documentation, no undocumented "magic" |

### 3.3 Technical / External System Stakeholders

| ID | Stakeholder | Role/Description | Key Interest | Key Expectation / Constraint Imposed |
|---|---|---|---|---|
| SH-08 | **Google Gemini API (Anthropic-equivalent third party)** | Provides AI doubt-solving and concept explanation | Responsible, policy-compliant usage | Rate limits, usage-based cost, content policy compliance, API stability |
| SH-09 | **Render (Hosting Provider)** | Hosts the deployed Django application | Platform stability, resource usage within tier limits | Free-tier cold starts, resource ceilings, deployment configuration compliance |
| SH-10 | **Neon PostgreSQL (Database Provider)** | Hosts the production database | Efficient, policy-compliant usage | Connection limits, storage limits on free/hobby tier |
| SH-11 | **Cloudinary (Media Storage Provider)** | Hosts uploaded images (profile pictures, question images) | Efficient storage/bandwidth usage | Storage quota and bandwidth limits on free tier |
| SH-12 | **GitHub** | Version control and collaboration platform | N/A (infrastructure) | Repository structure, commit hygiene, branch protection |

### 3.4 Academic Stakeholders

| ID | Stakeholder | Role/Description | Key Interest | Key Expectation |
|---|---|---|---|---|
| SH-13 | **Institution / University** | Grants the degree tied to this project | Program reputation, industry relevance of student work | Project aligns with learning outcomes, demonstrates competency |
| SH-14 | **Peer Students / Future Batches** | May reference this project as an example | Learning resource, benchmark | Well-documented process others can learn from |

---

## 4. Stakeholder Influence–Interest Matrix

This matrix helps decide how much attention and communication effort each stakeholder deserves — a standard project management technique (adapted from Mendelow's Matrix).

```
                    HIGH INFLUENCE
                          │
      Manage Closely      │      Keep Satisfied
   ┌──────────────────────┼──────────────────────┐
   │  SH-05 Project Guide  │  SH-08 Gemini API     │
   │  SH-06 Examiner       │  SH-09 Render         │
   │  SH-01 Student        │  SH-10 Neon           │
   │                        │  SH-11 Cloudinary     │
LOW├────────────────────────┼───────────────────────┤ HIGH
INT│  Monitor              │  Keep Informed         │INTEREST
ERE│  SH-12 GitHub         │  SH-02 Admin           │
ST │  SH-13 Institution    │  SH-03 Developer 1     │
   │  SH-14 Peers           │  SH-04 Developer 2     │
   │                        │  SH-07 Future Maint.   │
   └──────────────────────┼──────────────────────┘
                          │
                    LOW INFLUENCE
```

**Interpretation:**

- **Manage Closely (High Influence, High Interest):** The Student (your actual user, whose satisfaction determines product success) and your Project Guide/Examiner (who determine your grade) require the most direct engagement — through usability testing and regular documentation reviews respectively.
- **Keep Satisfied (High Influence, Lower day-to-day interest):** External APIs/platforms don't "care" about your project, but their limits and policies can break your system if ignored — so their constraints must be respected in design (see NFR-COST, NFR-SEC-07).
- **Keep Informed (High Interest, Lower influence):** You and your co-developer are highly interested but your individual influence over external constraints (API pricing, hosting limits) is low — you must design around them, not against them.
- **Monitor (Low Influence, Low Interest):** Institutional/peer stakeholders benefit passively from good documentation but don't need active management.

---

## 5. Communication & Engagement Plan

| Stakeholder | Communication Method | Frequency |
|---|---|---|
| Developer 1 & 2 | Daily standup (async chat or call), shared task board | Daily |
| Project Guide | Progress review meeting | Weekly |
| Students (via usability feedback, if a pilot group is available) | Informal feedback form / testing session | Once during Phase 4 (Testing) |
| External APIs/Platforms | Documentation monitoring for breaking changes | As needed, before integration work |

---

## Document Control

| Field | Value |
|---|---|
| Document ID | CC-STK-03 |
| Version | 1.0 |
| Created | 2026-07-29 |
| Last Updated | 2026-07-29 |
| Status | Draft |
| Depends On | CC-FRD-01, CC-NFR-02 |
| Storage Location | `docs/requirements/03_stakeholders.md` |

---

*End of Document — ConceptCode Stakeholders v1.0*
