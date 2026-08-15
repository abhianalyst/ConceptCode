# ConceptCode – AI Powered Adaptive Learning Platform
## Document 05: User Stories
**Version:** 1.0
**Phase:** Phase 0 – Requirement Analysis
**Status:** Draft – Pending Review
**Prepared By:** Development Team
**Date:** 2026-07-29

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [User Story Format](#2-user-story-format)
3. [Epic 1: Authentication & Onboarding](#epic-1-authentication--onboarding)
4. [Epic 2: Dashboard](#epic-2-dashboard)
5. [Epic 3: Syllabus Navigation](#epic-3-syllabus-navigation)
6. [Epic 4: Adaptive Practice](#epic-4-adaptive-practice)
7. [Epic 5: Mock Tests](#epic-5-mock-tests)
8. [Epic 6: AI Doubt Solver](#epic-6-ai-doubt-solver)
9. [Epic 7: AI Concept Explainer](#epic-7-ai-concept-explainer)
10. [Epic 8: Performance Analytics](#epic-8-performance-analytics)
11. [Epic 9: Weak Area Detection (ML)](#epic-9-weak-area-detection-ml)
12. [Epic 10: Study Planner](#epic-10-study-planner)
13. [Epic 11: Admin Content Management](#epic-11-admin-content-management)
14. [Epic 12: Notifications & Leaderboard](#epic-12-notifications--leaderboard)
15. [Story Point Summary & Prioritization](#15-story-point-summary--prioritization)

---

## 1. Introduction

### 1.1 Purpose
This document decomposes ConceptCode's functional requirements into user stories grouped by **Epic** (a large body of related work). Each story maps back to one or more FR IDs from Document 01, and forward to acceptance criteria that will become test cases in the Testing phase.

### 1.2 Story Point Scale
We use a simplified Fibonacci-like scale common in Agile teams, sized for a 2-developer team:

| Points | Meaning | Rough Effort |
|---|---|---|
| 1 | Trivial | < 2 hours |
| 2 | Small | Half day |
| 3 | Medium | 1 day |
| 5 | Large | 2–3 days |
| 8 | Very Large | 4–5 days (candidate for further breakdown) |

---

## 2. User Story Format

```
ID: US-XX
As a [persona], I want to [action], so that [benefit].

Acceptance Criteria:
- Given [context], when [action], then [expected result]

Linked FR: FR-XX-XX
Story Points: N
Priority: High / Medium / Low
```

---

## Epic 1: Authentication & Onboarding

### US-01: Student Registration
**As a** new student (Rohan), **I want to** create an account using my email and password, **so that** I can save my progress and access personalized features.

**Acceptance Criteria:**
- Given I am on the registration page, when I submit a valid name, unique email, and password (≥8 characters), then my account is created and a verification email is sent.
- Given I enter an email that already exists, when I submit the form, then I see an error: "An account with this email already exists."
- Given I submit a password shorter than 8 characters, when I submit the form, then I see a real-time validation error before submission.

**Linked FR:** FR-01-01, FR-01-02, FR-01-03, FR-01-04
**Story Points:** 3 | **Priority:** High

---

### US-02: Email Verification
**As a** newly registered student, **I want to** verify my email via a link, **so that** I can activate my account and log in.

**Acceptance Criteria:**
- Given I receive the verification email, when I click the link, then my account status changes to "verified" and I am redirected to the login page with a success message.
- Given I try to log in before verifying, when I submit correct credentials, then I see: "Please verify your email before logging in," with an option to resend the verification link.

**Linked FR:** FR-01-04, FR-01-05
**Story Points:** 3 | **Priority:** High

---

### US-03: Student Login
**As a** returning student (Ananya), **I want to** log in with my email and password, **so that** I can continue my preparation from where I left off.

**Acceptance Criteria:**
- Given valid, verified credentials, when I submit the login form, then I am redirected to my dashboard.
- Given invalid credentials, when I submit the form, then I see: "Invalid email or password" without revealing which field was wrong (security best practice).
- Given 5 consecutive failed attempts, when I try again, then my account is locked for 15 minutes with a clear message.

**Linked FR:** FR-01-06, FR-01-12
**Story Points:** 2 | **Priority:** High

---

### US-04: Password Reset
**As a** student (Ananya) who forgot my password, **I want to** reset it via email, **so that** I can regain access to my account.

**Acceptance Criteria:**
- Given I click "Forgot Password" and submit my registered email, when the request is processed, then a time-limited reset link is emailed to me.
- Given I click an expired reset link, when the page loads, then I see: "This link has expired. Please request a new one."
- Given I set a new valid password via the link, when I submit, then I can log in immediately with the new password.

**Linked FR:** FR-01-07
**Story Points:** 3 | **Priority:** High

---

### US-05: Profile Management
**As a** logged-in student, **I want to** update my name, profile picture, and phone number, **so that** my profile reflects accurate, current information.

**Acceptance Criteria:**
- Given I upload a profile picture, when it exceeds 5MB or is not a JPEG/PNG, then I see a validation error and the upload is rejected.
- Given I update my name, when I save, then the change reflects immediately across the dashboard greeting and profile.

**Linked FR:** FR-01-08, NFR-SEC-11
**Story Points:** 2 | **Priority:** Medium

---

## Epic 2: Dashboard

### US-06: View Personalized Dashboard
**As a** student (Meera), **I want to** see a summary of my performance the moment I log in, **so that** I immediately know where I stand without digging through menus.

**Acceptance Criteria:**
- Given I log in, when the dashboard loads, then I see cards for: today's questions attempted, overall accuracy, weekly study time, and leaderboard rank — within 3 seconds (NFR-PERF-01).
- Given I have no activity yet (new user), when the dashboard loads, then I see empty-state prompts guiding me to start a practice session, instead of blank/broken cards.

**Linked FR:** FR-02-01 to FR-02-05
**Story Points:** 5 | **Priority:** High

---

### US-07: See Subject-Wise Performance Chart
**As a** student (Meera), **I want to** see a visual breakdown of my performance by subject, **so that** I can quickly compare Physics, Chemistry, and Biology at a glance.

**Acceptance Criteria:**
- Given I have attempted questions in at least one subject, when the dashboard loads, then a Chart.js bar/radar chart displays accuracy per subject.
- Given I have zero attempts in a subject, when the chart renders, then that subject shows as 0% rather than being omitted (to avoid a misleading chart).

**Linked FR:** FR-02-06
**Story Points:** 3 | **Priority:** High

---

### US-08: See Weakest Topics on Dashboard
**As a** student (Ananya), **I want to** see my top weakest topics immediately on login, **so that** I know exactly what to focus on today without guessing.

**Acceptance Criteria:**
- Given the ML model has processed my performance data, when the dashboard loads, then I see my top 3 weakest topics, each clickable to start practicing that topic directly.
- Given I am a new user with insufficient data, when the dashboard loads, then this section shows a friendly message: "Complete a few practice sessions to unlock personalized insights."

**Linked FR:** FR-02-07, FR-10-04
**Story Points:** 5 | **Priority:** High

---

## Epic 3: Syllabus Navigation

### US-09: Browse Syllabus
**As a** first-time student (Rohan), **I want to** browse subjects, chapters, and topics in a structured view, **so that** I understand the full scope of what I need to study.

**Acceptance Criteria:**
- Given I navigate to the syllabus explorer, when the page loads, then I see all three subjects, each expandable into chapters and topics.
- Given a topic has been attempted before, when I view it, then I see my personal completion percentage displayed on that topic card.

**Linked FR:** FR-03-01 to FR-03-06
**Story Points:** 5 | **Priority:** High

---

### US-10: Identify Topics Needing Attention
**As a** student (Ananya), **I want to** see which topics are visually flagged as weak, **so that** I can prioritize my study time effectively.

**Acceptance Criteria:**
- Given my accuracy in a topic is below 60%, when I view the syllabus explorer, then that topic is visually marked (e.g., red badge: "Needs Attention").
- Given my accuracy improves above 60% after further practice, when I revisit the page, then the flag is automatically removed.

**Linked FR:** FR-03-07
**Story Points:** 3 | **Priority:** High

---

## Epic 4: Adaptive Practice

### US-11: Start a Practice Session
**As a** student (any persona), **I want to** start practicing questions for a specific topic, **so that** I can build mastery in that area.

**Acceptance Criteria:**
- Given I click "Practice" on a topic, when the session starts, then I am shown one question at a time with four options.
- Given I have already answered a question correctly in the last 7 days, when a new practice session starts, then that question is excluded from selection.

**Linked FR:** FR-05-01, FR-05-02, FR-05-11
**Story Points:** 5 | **Priority:** High

---

### US-12: Receive Adaptive Difficulty
**As a** student (Ananya), **I want to** be served questions that match my current skill level, **so that** I'm neither bored by easy questions nor overwhelmed by hard ones.

**Acceptance Criteria:**
- Given I answer 2 consecutive questions correctly, when the next question is served, then the ML model selects a higher difficulty level.
- Given I answer 2 consecutive questions incorrectly, when the next question is served, then the ML model selects a lower difficulty level.

**Linked FR:** FR-05-03
**Story Points:** 8 | **Priority:** High

---

### US-13: Get Immediate Feedback with Explanation
**As a** student (Rohan), **I want to** see immediately whether I was right or wrong, with an explanation, **so that** I learn from every question, not just my final score.

**Acceptance Criteria:**
- Given I submit an answer, when the result is processed, then I see correct/incorrect status and the full explanation within 1.5 seconds (NFR-PERF-02).
- Given the explanation contains a formula, when it is displayed, then it renders correctly using proper mathematical formatting (not garbled text).

**Linked FR:** FR-05-04, FR-05-05
**Story Points:** 3 | **Priority:** High

---

### US-14: View Session Summary
**As a** student, **I want to** see a summary at the end of my practice session, **so that** I understand how I performed overall.

**Acceptance Criteria:**
- Given I complete or exit a practice session, when the summary screen loads, then I see: total attempted, correct, incorrect, accuracy %, and time spent.

**Linked FR:** FR-05-10
**Story Points:** 2 | **Priority:** High

---

## Epic 5: Mock Tests

### US-15: Take a Full-Length Mock Test
**As a** student (Meera), **I want to** take a timed, full-length NEET mock test, **so that** I can simulate real exam conditions.

**Acceptance Criteria:**
- Given I start a Full NEET Mock, when the test loads, then I see 180 questions with a 200-minute countdown timer.
- Given the timer reaches zero, when time expires, then the test auto-submits without requiring my action.
- Given I navigate between questions, when I mark one "for review," then the question palette reflects this status visually.

**Linked FR:** FR-06-01 to FR-06-06
**Story Points:** 8 | **Priority:** High

---

### US-16: View Detailed Mock Test Results
**As a** student (Meera), **I want to** see a detailed breakdown of my mock test performance, **so that** I can analyze exactly where I lost marks.

**Acceptance Criteria:**
- Given I submit a mock test, when results are generated, then I see total score (with NEET +4/-1 marking), subject-wise breakdown, and time spent per question.
- Given I click on any question in the result, when it expands, then I see the correct answer and explanation, regardless of whether I answered correctly.

**Linked FR:** FR-06-07, FR-06-08
**Story Points:** 5 | **Priority:** High

---

## Epic 6: AI Doubt Solver

### US-17: Ask an AI a Doubt
**As a** student (Ananya), **I want to** type any NEET-related doubt and get an instant explanation, **so that** I don't have to wait until my next coaching class.

**Acceptance Criteria:**
- Given I type a question and submit, when the AI responds, then I see a formatted answer within 8 seconds for 95% of requests (NFR-PERF-04), with a loading indicator shown while waiting.
- Given the Gemini API fails or times out, when this happens, then I see a friendly error message: "Something went wrong. Please try again," rather than a broken page.
- Given I ask something unrelated to NEET/academics, when the AI responds, then it politely declines and redirects me to academic topics.

**Linked FR:** FR-07-01 to FR-07-05, FR-07-09, FR-07-10
**Story Points:** 8 | **Priority:** High

---

### US-18: View Doubt History
**As a** student, **I want to** revisit my previously asked doubts, **so that** I can review explanations without re-asking the same question.

**Acceptance Criteria:**
- Given I have asked doubts before, when I open "My Doubts," then I see a paginated list, most recent first.
- Given I delete a doubt entry, when I confirm deletion, then it is permanently removed from my history.

**Linked FR:** FR-07-06 to FR-07-08
**Story Points:** 3 | **Priority:** Medium

---

## Epic 7: AI Concept Explainer

### US-19: Get AI Explanation for a Topic
**As a** first-time student (Rohan), **I want to** get a structured AI explanation of any topic, **so that** I can understand it from scratch without external resources.

**Acceptance Criteria:**
- Given I click "Explain This Topic with AI" on a topic page, when the AI responds, then I see a structured explanation: Overview, Key Concepts, Formulas (if applicable), Common Mistakes, and NEET Relevance.
- Given the same topic was explained within the last 24 hours (for any user), when I request it, then the cached version is served instantly instead of calling the API again.

**Linked FR:** FR-08-01 to FR-08-05
**Story Points:** 5 | **Priority:** High

---

## Epic 8: Performance Analytics

### US-20: Analyze Deep Performance Trends
**As a** high-achiever student (Meera), **I want to** see granular analytics across time, subject, chapter, and difficulty, **so that** I can identify precise, marginal improvement opportunities.

**Acceptance Criteria:**
- Given I visit the analytics page, when it loads, then I see: 30-day accuracy trend, subject-wise radar chart, chapter-wise sortable table, and difficulty-wise breakdown.
- Given I filter by a specific subject and date range, when I apply the filter, then all charts update to reflect only that filtered data.

**Linked FR:** FR-09-01 to FR-09-07
**Story Points:** 8 | **Priority:** High

---

## Epic 9: Weak Area Detection (ML)

### US-21: Receive ML-Based Topic Recommendations
**As a** student (Ananya), **I want to** be told exactly which topic to practice next, **so that** I don't waste time deciding what to study.

**Acceptance Criteria:**
- Given I complete a practice session or mock test, when the ML model reprocesses my data, then my weak/moderate/strong topic classifications update accordingly.
- Given the ML model is temporarily unavailable, when weak areas are requested, then the system falls back to rule-based detection (accuracy < 50%) without errors (FR-10-07).

**Linked FR:** FR-10-01 to FR-10-07
**Story Points:** 8 | **Priority:** High

---

## Epic 10: Study Planner

### US-22: Create a Personal Study Plan
**As a** first-time student (Rohan), **I want to** schedule topics with target dates, **so that** I have a clear, guided path through the syllabus.

**Acceptance Criteria:**
- Given I select topics and assign target dates, when I save the plan, then it appears in a calendar-style view.
- Given I achieve ≥80% accuracy in a planned topic, when this threshold is met, then the planner automatically marks it "Completed."

**Linked FR:** FR-11-01 to FR-11-03
**Story Points:** 5 | **Priority:** Medium

---

## Epic 11: Admin Content Management

### US-23: Bulk Upload Questions
**As an** administrator (Mr. Iyer), **I want to** upload hundreds of questions via a CSV file, **so that** I don't have to enter them manually one at a time.

**Acceptance Criteria:**
- Given I upload a correctly formatted CSV, when processing completes, then all valid questions are added and I see a success count.
- Given the CSV contains malformed rows, when processing completes, then I see a clear report listing which rows failed and why, without corrupting valid rows.

**Linked FR:** FR-04-06, FR-12-04
**Story Points:** 5 | **Priority:** Medium

---

### US-24: Manage Student Accounts
**As an** administrator, **I want to** search, view, and deactivate student accounts, **so that** I can manage abuse or support requests efficiently.

**Acceptance Criteria:**
- Given I search for a student by name or email, when results load, then I see matching accounts with status and quick actions.
- Given I deactivate an account, when I confirm, then that student can no longer log in, and sees an appropriate message if they try.

**Linked FR:** FR-12-02
**Story Points:** 3 | **Priority:** Medium

---

## Epic 12: Notifications & Leaderboard

### US-25: Receive Milestone Notifications
**As a** student (Ananya), **I want to** be notified when I hit a milestone, **so that** I feel motivated to keep going.

**Acceptance Criteria:**
- Given I reach a milestone (e.g., 7-day streak), when it is triggered, then an in-app notification appears and the unread count updates in the navbar.

**Linked FR:** FR-13-01, FR-13-03
**Story Points:** 3 | **Priority:** Low

---

### US-26: View Leaderboard Ranking
**As a** competitive student (Meera), **I want to** see my rank among all students, **so that** I can gauge my relative standing.

**Acceptance Criteria:**
- Given I visit the leaderboard, when it loads, then I see my current rank, accuracy, and questions attempted, alongside the top-ranked students.
- Given I filter by subject, when I apply the filter, then the leaderboard recalculates rankings for that subject only.

**Linked FR:** FR-14-01 to FR-14-05
**Story Points:** 3 | **Priority:** Low

---

## 15. Story Point Summary & Prioritization

| Epic | Stories | Total Points | Priority Weight |
|---|---|---|---|
| Epic 1: Authentication & Onboarding | 5 | 13 | High |
| Epic 2: Dashboard | 3 | 13 | High |
| Epic 3: Syllabus Navigation | 2 | 8 | High |
| Epic 4: Adaptive Practice | 4 | 18 | High |
| Epic 5: Mock Tests | 2 | 13 | High |
| Epic 6: AI Doubt Solver | 2 | 11 | High/Medium |
| Epic 7: AI Concept Explainer | 1 | 5 | High |
| Epic 8: Performance Analytics | 1 | 8 | High |
| Epic 9: Weak Area Detection (ML) | 1 | 8 | High |
| Epic 10: Study Planner | 1 | 5 | Medium |
| Epic 11: Admin Content Management | 2 | 8 | Medium |
| Epic 12: Notifications & Leaderboard | 2 | 6 | Low |
| **TOTAL** | **26** | **116** | — |

**Why this matters for your 1-month timeline:** With 116 story points across 2 developers, and assuming roughly 2-week sprints, this table is your sprint-planning input. High-priority epics (Auth, Dashboard, Practice, Mock Tests, AI features, Analytics, ML) total roughn ~84 points and should occupy Sprint 1–2. Medium/Low epics (Study Planner, Admin extras, Notifications, Leaderboard) total ~19 points and are the first candidates to trim if the timeline gets tight — this is exactly what MVP scoping is for.

---

## Document Control

| Field | Value |
|---|---|
| Document ID | CC-US-05 |
| Version | 1.0 |
| Created | 2026-07-29 |
| Last Updated | 2026-07-29 |
| Status | Draft |
| Depends On | CC-FRD-01, CC-PER-04 |
| Storage Location | `docs/requirements/05_user_stories.md` |

---

*End of Document — ConceptCode User Stories v1.0*
