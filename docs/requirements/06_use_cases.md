# ConceptCode – AI Powered Adaptive Learning Platform
## Document 06: Use Cases
**Version:** 1.0
**Phase:** Phase 0 – Requirement Analysis
**Status:** Draft – Pending Review
**Prepared By:** Development Team
**Date:** 2026-07-29

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Use Case Diagram (Actor Overview)](#2-use-case-diagram-actor-overview)
3. [Fully Detailed Use Cases](#3-fully-detailed-use-cases)
   - [UC-01: Take a Mock Test](#uc-01-take-a-mock-test)
   - [UC-02: Adaptive Practice Session](#uc-02-adaptive-practice-session)
   - [UC-03: Ask the AI Doubt Solver](#uc-03-ask-the-ai-doubt-solver)
   - [UC-04: Weak Area Detection Update](#uc-04-weak-area-detection-update)
4. [Compact Use Cases](#4-compact-use-cases)
5. [Use Case Traceability](#5-use-case-traceability)

---

## 1. Introduction

### 1.1 Purpose
This document specifies, in detail, the interaction flows between system actors (Student, Administrator, ML Engine, Gemini AI) and ConceptCode, including exception and alternate paths.

### 1.2 Use Case Notation
Each fully detailed use case follows this structure:

| Field | Meaning |
|---|---|
| **Use Case ID** | Unique identifier |
| **Actor(s)** | Who initiates or participates |
| **Preconditions** | What must be true before this use case starts |
| **Main Success Scenario** | The step-by-step "happy path" |
| **Alternate Flows** | Valid variations of the happy path |
| **Exception Flows** | Error/failure handling |
| **Postconditions** | System state after successful completion |

---

## 2. Use Case Diagram (Actor Overview)

```
                        ┌─────────────────────────────┐
                        │        ConceptCode           │
                        │                               │
   ┌─────────┐          │  • Register / Login           │
   │ Student │──────────┼─▶• Browse Syllabus             │
   └─────────┘          │  • Adaptive Practice          │◀──────┐
                         │  • Take Mock Test             │       │
                         │  • Ask AI Doubt               │       │ predicts
                         │  • Get AI Concept Explanation │       │ difficulty /
                         │  • View Analytics             │       │ weak areas
                         │  • View/Edit Study Plan       │       │
                         │  • View Leaderboard           │  ┌────┴─────┐
                         │                               │  │ ML Engine │
   ┌─────────┐           │                               │  └──────────┘
   │  Admin  │───────────┼─▶• Manage Questions            │
   └─────────┘           │  • Manage Users               │  ┌──────────┐
                         │  • Bulk Upload Content        │  │Gemini AI │
                         │  • View Platform Stats        │  │  (API)   │
                         │                               │◀─┼──────────┘
                         └─────────────────────────────┘   answers doubts /
                                                             explains concepts
```

**Actors:**
- **Student** — Primary human actor, initiates most use cases
- **Administrator** — Secondary human actor, manages content/users
- **ML Engine** — System actor (internal), triggered automatically after student activity
- **Gemini AI** — External system actor, invoked by the system on behalf of the student

---

## 3. Fully Detailed Use Cases

---

### UC-01: Take a Mock Test

| Field | Detail |
|---|---|
| **Use Case ID** | UC-01 |
| **Actor(s)** | Student (primary) |
| **Related User Story** | US-15, US-16 |
| **Related FRs** | FR-06-01 to FR-06-10 |
| **Preconditions** | Student is logged in and verified; question bank has sufficient questions across all chapters |
| **Trigger** | Student clicks "Start Mock Test" and selects a test type |

**Main Success Scenario:**

1. Student navigates to the Mock Test section.
2. Student selects test type: Full NEET Mock or Subject Mock.
3. System displays test instructions (duration, marking scheme, question count) and a "Start Test" confirmation.
4. Student confirms and starts the test.
5. System randomly selects questions from the question bank matching the test type's subject/chapter coverage rules.
6. System displays the test interface: question palette, timer (counting down), navigation controls, and the first question.
7. Student answers questions, navigating freely, optionally marking questions "for review."
8. System auto-saves student's answers and current state every 30 seconds (NFR-REL-03).
9. Student reviews the question palette to confirm attempt status.
10. Student clicks "Submit Test" and confirms via a dialog ("Are you sure? X questions are unattempted.").
11. System calculates the score using the NEET marking scheme (+4 correct, −1 incorrect, 0 unattempted).
12. System generates and displays the detailed result report (score, subject-wise breakdown, time-per-question, answer review).
13. System stores the complete test attempt record permanently for historical analytics.
14. System triggers the ML Engine (UC-04) asynchronously to update weak area classifications based on this new data.

**Alternate Flows:**

- **A1 — Timer Expires:** At step 7-9, if the countdown timer reaches zero, the system automatically submits the test using whatever answers were recorded, and proceeds to step 11. No confirmation dialog is shown.
- **A2 — Student Marks for Review:** At step 7, student can mark a question "for review" instead of/in addition to answering; the question palette updates its color/status accordingly.
- **A3 — Student Pauses Browser Tab:** If the student switches tabs or the browser loses focus, the timer continues running server-side (never trust client-side time alone) to prevent time manipulation.

**Exception Flows:**

- **E1 — Network Disconnect During Test:** If the student's connection drops between auto-saves, the system retries the auto-save silently on reconnect; if the student reloads mid-test, the system restores their last auto-saved state and remaining time (calculated server-side from test start timestamp, not client clock).
- **E2 — Insufficient Questions in Bank:** If the question bank lacks enough questions to build a valid full mock test, the system prevents test creation and shows the administrator-facing error in logs, and shows the student: "This test is temporarily unavailable. Please try again later."
- **E3 — Duplicate Submission:** If the student double-clicks "Submit," the system ensures idempotency — only one attempt record is created, using a server-side submission lock.

**Postconditions:**
- A complete `TestAttempt` record exists in the database with all question-level responses.
- The student's dashboard and analytics reflect the new attempt immediately.
- The ML Engine has been queued to reprocess this student's performance profile.

---

### UC-02: Adaptive Practice Session

| Field | Detail |
|---|---|
| **Use Case ID** | UC-02 |
| **Actor(s)** | Student (primary), ML Engine (supporting) |
| **Related User Story** | US-11, US-12, US-13, US-14 |
| **Related FRs** | FR-05-01 to FR-05-11 |
| **Preconditions** | Student is logged in; selected topic has at least one active question |
| **Trigger** | Student clicks "Practice" on a topic |

**Main Success Scenario:**

1. Student selects a topic and clicks "Start Practice."
2. System initializes a practice session, defaulting to Medium difficulty (or the student's last known difficulty level for that topic, if available).
3. System excludes questions the student answered correctly within the last 7 days (FR-05-11).
4. System serves one question to the student.
5. Student submits an answer (or skips, if allowed).
6. System evaluates correctness and immediately displays result + explanation.
7. System records the attempt: question ID, answer, correctness, time taken, difficulty served.
8. System calls the ML Engine's lightweight inference function to determine the next question's difficulty based on the student's recent streak (e.g., 2 correct in a row → increase difficulty; 2 incorrect in a row → decrease).
9. Steps 4-8 repeat until the student ends the session or exhausts available questions.
10. Student clicks "End Session."
11. System displays the session summary (total attempted, correct, incorrect, accuracy, time spent).
12. System triggers the ML Engine (UC-04) asynchronously to update the student's topic-level performance classification.

**Alternate Flows:**

- **A1 — Student Bookmarks a Question:** At step 5, before or after answering, student can bookmark the question for later review; this does not interrupt the session flow.
- **A2 — Student Pauses Session:** At any point, student can click "Pause"; system preserves session state, allowing resume later from the same point (FR-05-09).
- **A3 — No Questions Remain:** If the topic runs out of unattempted/eligible questions, system shows: "You've completed all available questions in this topic for now!" and proceeds to step 10.

**Exception Flows:**

- **E1 — ML Engine Unavailable:** If step 8's ML inference call fails or times out, the system falls back to a simple rule (repeat last difficulty level) so the session is never blocked.
- **E2 — Empty Answer Submission:** If the student attempts to submit without selecting an option, the system prevents submission client-side and shows: "Please select an answer."

**Postconditions:**
- All question attempts in the session are recorded in the database.
- The topic's completion percentage for this student is updated.
- The ML Engine has fresh data for the next weak-area classification cycle.

---

### UC-03: Ask the AI Doubt Solver

| Field | Detail |
|---|---|
| **Use Case ID** | UC-03 |
| **Actor(s)** | Student (primary), Gemini AI (external system) |
| **Related User Story** | US-17, US-18 |
| **Related FRs** | FR-07-01 to FR-07-10 |
| **Preconditions** | Student is logged in; student has not exceeded hourly AI request rate limit (NFR-SEC-10) |
| **Trigger** | Student types a doubt and clicks "Ask" |

**Main Success Scenario:**

1. Student navigates to the Doubt Solver page.
2. Student types their doubt (up to 1000 characters) into the input field.
3. Student clicks "Ask."
4. System displays a loading indicator.
5. System constructs a prompt combining the student's question with a NEET-specific system context (subject scope, tone, format instructions).
6. System sends the request to the Gemini API with a 10-second timeout.
7. Gemini API returns a generated response.
8. System renders the response with markdown formatting (headings, bullet points, bold).
9. System saves the doubt-answer pair to the database, linked to the student's account.
10. System displays the answer to the student, clearly labeled "AI-generated" (NFR-AI-04).

**Alternate Flows:**

- **A1 — Off-Topic Query:** At step 7, if the query is unrelated to NEET/academics, the Gemini response (guided by the system prompt) politely declines and redirects the student to ask academic questions; this response is still saved and displayed normally.
- **A2 — Student Views History:** Independent of a new query, student can navigate to "My Doubts" to view paginated past queries (most recent first) and delete individual entries.

**Exception Flows:**

- **E1 — Gemini API Timeout:** If step 6 exceeds 10 seconds, the system performs exactly one retry (NFR-AI-03). If the retry also fails, the system displays: "Something went wrong. Please try again in a moment," and does not save an empty record.
- **E2 — Gemini API Returns Error/Content Policy Block:** System catches the error, logs it server-side (without exposing internal details to the user), and shows a generic friendly error message.
- **E3 — Rate Limit Exceeded:** If the student has made 30+ AI requests in the past hour, the system blocks the new request and shows: "You've reached your hourly limit for AI questions. Please try again later," before calling the Gemini API (to save cost).

**Postconditions:**
- A `DoubtQuery` record is created (on success) linking student, question text, AI response, and timestamp.
- No orphaned/empty records are created on failure paths.

---

### UC-04: Weak Area Detection Update

| Field | Detail |
|---|---|
| **Use Case ID** | UC-04 |
| **Actor(s)** | ML Engine (primary, system-triggered), Student (indirect beneficiary) |
| **Related User Story** | US-08, US-21 |
| **Related FRs** | FR-10-01 to FR-10-07 |
| **Preconditions** | Student has at least one recorded practice/test attempt |
| **Trigger** | Asynchronous — fired automatically after UC-01 (Mock Test) or UC-02 (Practice Session) completion |

**Main Success Scenario:**

1. System receives a trigger event (practice session ended or mock test submitted) with the student's ID.
2. System aggregates the student's performance data per topic: accuracy, attempt count, difficulty distribution, average time per question.
3. System loads the trained, serialized (Joblib) classification model.
4. System runs inference, classifying each topic the student has attempted as Strong, Moderate, or Weak.
5. System updates the student's `TopicPerformance` records with the new classification.
6. System recalculates the top 5 weakest topics per subject for that student.
7. Updated classifications become immediately available to the Dashboard (UC covered in Epic 2) and Analytics pages on next load.

**Alternate Flows:**

- **A1 — Insufficient Data:** If the student has fewer than a minimum threshold of attempts in a topic (e.g., 5 questions), that topic is excluded from classification and instead shown as "Not enough data yet."

**Exception Flows:**

- **E1 — Model File Missing/Corrupted:** System catches the load failure, logs it, and falls back to rule-based classification: accuracy < 50% → Weak, 50-75% → Moderate, > 75% → Strong (FR-10-07). This ensures the feature never fully breaks even if ML infrastructure fails.
- **E2 — Processing Failure Mid-Batch:** If classification fails for one topic, the system continues processing remaining topics rather than aborting the entire update (partial success is better than total failure).

**Postconditions:**
- The student's `TopicPerformance` table reflects current classifications.
- This use case never blocks or delays the student-facing use cases (UC-01, UC-02) that trigger it — it always runs asynchronously.

---

## 4. Compact Use Cases

The following use cases follow simpler flows and are documented concisely, following the same principles (main flow + key exceptions) without full elaboration.

| ID | Use Case | Actor | Main Flow Summary | Key Exception |
|---|---|---|---|---|
| UC-05 | Register Account | Student | Fill form → validate → create account → send verification email | Duplicate email → show inline error |
| UC-06 | Login | Student | Enter credentials → validate → redirect to dashboard | 5 failed attempts → 15-min lockout |
| UC-07 | Reset Password | Student | Request reset → receive email → set new password | Expired link → prompt to request new one |
| UC-08 | Browse Syllabus | Student | Select subject → view chapters → view topics with completion % | No questions in topic → show "Coming Soon" |
| UC-09 | View Performance Analytics | Student | Load analytics page → view charts → apply filters | No data yet → show empty-state guidance |
| UC-10 | Get AI Concept Explanation | Student, Gemini AI | Click "Explain with AI" → check cache → call API if not cached → render structured response | Cache hit → serve instantly, skip API call |
| UC-11 | Create Study Plan | Student | Select topics + dates → save plan → view calendar | Overlapping dates → allow but flag as heavy day |
| UC-12 | Bulk Upload Questions (Admin) | Administrator | Upload CSV → validate rows → import valid rows → show report | Malformed rows → skip + report, don't abort |
| UC-13 | Manage Question (Admin) | Administrator | Search/select question → edit fields → save | Invalid data (e.g., no correct answer) → block save |
| UC-14 | Manage Student Account (Admin) | Administrator | Search student → view profile → activate/deactivate | Deactivated student attempts login → blocked with message |
| UC-15 | View Leaderboard | Student | Load leaderboard → view rank → filter by subject | New student, no rank yet → show "Unranked" |
| UC-16 | Receive Notification | System, Student | Milestone triggered → notification created → badge count updates | Student has notifications disabled (future) → skip |

---

## 5. Use Case Traceability

| Use Case | Linked User Stories | Linked FRs | Primary Persona |
|---|---|---|---|
| UC-01 Mock Test | US-15, US-16 | FR-06-01 to FR-06-10 | Meera |
| UC-02 Adaptive Practice | US-11 to US-14 | FR-05-01 to FR-05-11 | Ananya |
| UC-03 AI Doubt Solver | US-17, US-18 | FR-07-01 to FR-07-10 | Ananya, Rohan |
| UC-04 Weak Area Detection | US-08, US-21 | FR-10-01 to FR-10-07 | Ananya |
| UC-05 Register | US-01 | FR-01-01 to FR-01-04 | Rohan |
| UC-06 Login | US-03 | FR-01-06, FR-01-12 | All students |
| UC-07 Reset Password | US-04 | FR-01-07 | All students |
| UC-08 Browse Syllabus | US-09, US-10 | FR-03-01 to FR-03-07 | Rohan |
| UC-09 Analytics | US-20 | FR-09-01 to FR-09-07 | Meera |
| UC-10 AI Concept Explainer | US-19 | FR-08-01 to FR-08-05 | Rohan |
| UC-11 Study Plan | US-22 | FR-11-01 to FR-11-03 | Rohan |
| UC-12 Bulk Upload | US-23 | FR-04-06, FR-12-04 | Mr. Iyer |
| UC-13 Manage Question | — | FR-04-05, FR-12-03 | Mr. Iyer |
| UC-14 Manage Student | US-24 | FR-12-02 | Mr. Iyer |
| UC-15 Leaderboard | US-26 | FR-14-01 to FR-14-05 | Meera |
| UC-16 Notifications | US-25 | FR-13-01, FR-13-03 | Ananya |

---

## Document Control

| Field | Value |
|---|---|
| Document ID | CC-UC-06 |
| Version | 1.0 |
| Created | 2026-07-29 |
| Last Updated | 2026-07-29 |
| Status | Draft |
| Depends On | CC-FRD-01, CC-US-05 |
| Storage Location | `docs/requirements/06_use_cases.md` |

---

*End of Document — ConceptCode Use Cases v1.0*
