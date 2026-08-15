---
output:
  html_document: default
  pdf_document: default
---
# ConceptCode – AI Powered Adaptive Learning Platform
## Document 01: Functional Requirements
**Version:** 1.0  
**Phase:** Phase 0 – Requirement Analysis  
**Status:** Draft – Pending Review  
**Prepared By:** Development Team  
**Date:** 2026-07-29  

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [System Overview](#2-system-overview)
3. [User Roles and Access Levels](#3-user-roles-and-access-levels)
4. [Functional Requirements by Module](#4-functional-requirements-by-module)
   - [FR-01: Authentication and User Management](#fr-01-authentication-and-user-management)
   - [FR-02: Student Dashboard](#fr-02-student-dashboard)
   - [FR-03: Subject and Topic Management](#fr-03-subject-and-topic-management)
   - [FR-04: Question Bank](#fr-04-question-bank)
   - [FR-05: Adaptive Practice Engine](#fr-05-adaptive-practice-engine)
   - [FR-06: Mock Test Module](#fr-06-mock-test-module)
   - [FR-07: AI Doubt Solver](#fr-07-ai-doubt-solver)
   - [FR-08: AI Concept Explainer](#fr-08-ai-concept-explainer)
   - [FR-09: Performance Analytics](#fr-09-performance-analytics)
   - [FR-10: Weak Area Detection (ML)](#fr-10-weak-area-detection-ml)
   - [FR-11: Study Planner](#fr-11-study-planner)
   - [FR-12: Admin Panel](#fr-12-admin-panel)
   - [FR-13: Notifications](#fr-13-notifications)
   - [FR-14: Leaderboard](#fr-14-leaderboard)
5. [Requirement Traceability Matrix (RTM)](#5-requirement-traceability-matrix-rtm)

---

## 1. Introduction

### 1.1 Purpose
This document defines the complete set of functional requirements for **ConceptCode v1.0**, an AI-powered adaptive learning platform designed to assist NEET aspirants in structured, personalized preparation. It serves as the foundational reference for system design, development, testing, and evaluation.

### 1.2 Scope
ConceptCode v1.0 (MVP) will be a web-based platform accessible via modern browsers. It will support authenticated student and administrator users. The platform will integrate Google Gemini AI for intelligent tutoring and Scikit-Learn-based machine learning for adaptive difficulty and weak area detection.

### 1.3 Definitions

| Term | Definition |
|---|---|
| NEET | National Eligibility cum Entrance Test – a medical entrance exam in India |
| Adaptive | Automatically adjusting difficulty or content based on student performance |
| ML | Machine Learning |
| AI | Artificial Intelligence (Google Gemini API in this context) |
| MVP | Minimum Viable Product |
| FR | Functional Requirement |
| Admin | Platform administrator with full access |
| Student | Registered learner using the platform |

---

## 2. System Overview

ConceptCode is structured around a core learning loop:

```
Student Registers → Attempts Practice/Tests → System Tracks Performance
       ↓                                                 ↓
AI Explains Doubts ← Weak Areas Identified ← ML Analyzes Data
       ↓
Student Improves → Dashboard Reflects Progress → Repeat
```

The platform covers three NEET subjects: **Physics**, **Chemistry**, and **Biology (Botany + Zoology)**.

---

## 3. User Roles and Access Levels

| Role | Description | Access Level |
|---|---|---|
| **Student** | Registered NEET aspirant using the platform for preparation | Standard |
| **Administrator** | Platform manager responsible for content and user management | Full |

> Note: A Teacher/Mentor role is explicitly out of scope for v1.0. It may be introduced in v2.0.

---

## 4. Functional Requirements by Module

Each requirement follows this format:

> **FR-XX-YY** | Priority: High / Medium / Low | Status: In Scope

---

### FR-01: Authentication and User Management

**Module Purpose:** Allow users to securely register, log in, and manage their accounts.

| ID | Requirement | Priority |
|---|---|---|
| FR-01-01 | The system shall allow a new student to register using their full name, email address, and password. | High |
| FR-01-02 | The system shall validate that the email address is unique at the time of registration. | High |
| FR-01-03 | The system shall enforce a minimum password length of 8 characters during registration. | High |
| FR-01-04 | The system shall send an email verification link to the student upon successful registration. | High |
| FR-01-05 | The system shall not allow login until the student's email is verified. | High |
| FR-01-06 | The system shall allow a registered student to log in using their email and password. | High |
| FR-01-07 | The system shall allow a student to reset their password via a time-limited email link. | High |
| FR-01-08 | The system shall allow a logged-in student to update their profile information (name, profile picture, phone number). | Medium |
| FR-01-09 | The system shall allow a logged-in student to change their password from the profile settings page. | Medium |
| FR-01-10 | The system shall allow a student to log out, invalidating their session immediately. | High |
| FR-01-11 | The system shall implement Django's built-in CSRF protection on all forms. | High |
| FR-01-12 | The system shall lock an account for 15 minutes after 5 consecutive failed login attempts. | Medium |

---

### FR-02: Student Dashboard

**Module Purpose:** Provide the student with a personalized overview of their progress, activity, and next recommended actions upon login.

| ID | Requirement | Priority |
|---|---|---|
| FR-02-01 | The dashboard shall display a personalized greeting with the student's name. | Medium |
| FR-02-02 | The dashboard shall display a summary card showing total questions attempted today. | High |
| FR-02-03 | The dashboard shall display a summary card showing the student's current overall accuracy percentage. | High |
| FR-02-04 | The dashboard shall display a summary card showing total study time logged this week. | Medium |
| FR-02-05 | The dashboard shall display a summary card showing the student's current rank on the leaderboard. | Medium |
| FR-02-06 | The dashboard shall display a subject-wise performance chart (Physics, Chemistry, Biology) using Chart.js. | High |
| FR-02-07 | The dashboard shall display a list of the student's top 3 weakest topics (generated by the ML module). | High |
| FR-02-08 | The dashboard shall display a "Continue Where You Left Off" section showing the last accessed topic or test. | Medium |
| FR-02-09 | The dashboard shall display upcoming scheduled mock test reminders if any are scheduled. | Low |
| FR-02-10 | The dashboard shall display a streak counter showing consecutive days of activity. | Medium |

---

### FR-03: Subject and Topic Management

**Module Purpose:** Organize the NEET syllabus into a structured hierarchy of Subjects → Chapters → Topics that students can browse and access.

| ID | Requirement | Priority |
|---|---|---|
| FR-03-01 | The system shall organize content under three subjects: Physics, Chemistry, and Biology. | High |
| FR-03-02 | Each subject shall be divided into chapters following the official NEET syllabus. | High |
| FR-03-03 | Each chapter shall contain one or more topics. | High |
| FR-03-04 | A student shall be able to browse all subjects, chapters, and topics from a syllabus explorer page. | High |
| FR-03-05 | Each topic page shall display the topic name, chapter, subject, and the number of available questions. | High |
| FR-03-06 | Each topic shall show the student's personal completion percentage (based on questions attempted). | High |
| FR-03-07 | The system shall visually highlight topics where the student's accuracy is below 60% as "Needs Attention". | High |
| FR-03-08 | The system shall allow administrators to add, edit, and delete subjects, chapters, and topics. | High |

---

### FR-04: Question Bank

**Module Purpose:** Maintain a structured, tagged database of NEET-level multiple-choice questions used across all practice and test modules.

| ID | Requirement | Priority |
|---|---|---|
| FR-04-01 | Each question shall contain: question text, four options (A, B, C, D), correct answer, explanation, subject, chapter, topic, difficulty level, and year tag (if from a previous NEET paper). | High |
| FR-04-02 | Difficulty levels shall be: Easy, Medium, Hard. | High |
| FR-04-03 | The system shall support questions with plain text and LaTeX-formatted mathematical expressions. | High |
| FR-04-04 | The system shall support questions containing images (stored on Cloudinary). | Medium |
| FR-04-05 | Administrators shall be able to add, edit, deactivate, and delete questions via the admin panel. | High |
| FR-04-06 | Administrators shall be able to bulk upload questions via a CSV file. | Medium |
| FR-04-07 | The system shall prevent duplicate questions from being added (based on question text similarity check or unique ID). | Medium |
| FR-04-08 | The system shall tag questions with their source (e.g., NEET 2020, NEET 2022, Custom). | Low |

---

### FR-05: Adaptive Practice Engine

**Module Purpose:** Allow students to practice questions topic-by-topic with the system intelligently selecting question difficulty based on the student's current performance.

| ID | Requirement | Priority |
|---|---|---|
| FR-05-01 | A student shall be able to start a practice session for any topic. | High |
| FR-05-02 | During a practice session, the system shall present one question at a time. | High |
| FR-05-03 | The system shall use the ML-based adaptive difficulty model to select the next question's difficulty based on recent performance. | High |
| FR-05-04 | After each answer is submitted, the system shall immediately display whether the answer was correct or incorrect. | High |
| FR-05-05 | After each answer, the system shall display the correct answer and its full explanation. | High |
| FR-05-06 | The student shall have the option to bookmark any question during a practice session. | Medium |
| FR-05-07 | The student shall have the option to report a question as incorrect or unclear. | Low |
| FR-05-08 | The practice session shall record: question ID, student answer, correctness, time taken per question, and difficulty level served. | High |
| FR-05-09 | A student shall be able to pause and resume a practice session. | Medium |
| FR-05-10 | At the end of a practice session, the system shall display a session summary: total attempted, correct, incorrect, accuracy, and time spent. | High |
| FR-05-11 | The system shall not repeat a question the student has already answered correctly in the same topic session (within 7 days). | Medium |

---

### FR-06: Mock Test Module

**Module Purpose:** Simulate the real NEET examination environment with timed, full-length or subject-specific tests.

| ID | Requirement | Priority |
|---|---|---|
| FR-06-01 | The system shall offer two types of mock tests: Full NEET Mock (180 questions, 200 minutes) and Subject Mock (60 questions per subject, 70 minutes). | High |
| FR-06-02 | Mock test questions shall be randomly selected from the question bank, covering all chapters of the respective subject(s). | High |
| FR-06-03 | The mock test interface shall display a countdown timer that auto-submits when time expires. | High |
| FR-06-04 | The mock test shall implement NEET marking scheme: +4 for correct, -1 for incorrect, 0 for unattempted. | High |
| FR-06-05 | During a mock test, the student shall be able to mark questions for review and navigate between questions freely. | High |
| FR-06-06 | The system shall display a question palette showing attempt status (Answered, Not Answered, Marked for Review, Not Visited). | High |
| FR-06-07 | On submission, the system shall generate a detailed result report showing: score, rank estimate, subject-wise breakdown, time per question, and correct/incorrect answers with explanations. | High |
| FR-06-08 | The system shall store all mock test attempts in the database for historical performance tracking. | High |
| FR-06-09 | A student shall be able to view and review all past mock test attempts from their profile. | Medium |
| FR-06-10 | The system shall prevent a student from accessing mock test questions outside the test interface. | Medium |

---

### FR-07: AI Doubt Solver

**Module Purpose:** Allow students to ask any NEET-related doubt in natural language and receive an accurate, contextual explanation powered by Google Gemini AI.

| ID | Requirement | Priority |
|---|---|---|
| FR-07-01 | The system shall provide a dedicated Doubt Solver page accessible from the main navigation. | High |
| FR-07-02 | A student shall be able to type a question or doubt in a text input field (up to 1000 characters). | High |
| FR-07-03 | The system shall send the student's query to the Google Gemini API with a NEET-specific system prompt context. | High |
| FR-07-04 | The system shall display the AI-generated response in a formatted, readable manner (supporting markdown rendering). | High |
| FR-07-05 | The system shall display a loading indicator while waiting for the AI response. | Medium |
| FR-07-06 | Each doubt-answer pair shall be saved to the database, linked to the student's account. | Medium |
| FR-07-07 | A student shall be able to view their full doubt history (paginated, most recent first). | Medium |
| FR-07-08 | A student shall be able to delete individual entries from their doubt history. | Low |
| FR-07-09 | The system shall gracefully handle API failures and display a user-friendly error message. | High |
| FR-07-10 | The doubt solver shall be limited to educational queries; the system prompt shall instruct the model to decline off-topic requests. | High |

---

### FR-08: AI Concept Explainer

**Module Purpose:** Allow students to request a structured AI-generated explanation of any NEET topic, breaking it down into digestible sections.

| ID | Requirement | Priority |
|---|---|---|
| FR-08-01 | Each topic page shall contain an "Explain This Topic with AI" button. | High |
| FR-08-02 | On clicking, the system shall call the Google Gemini API with the topic name and subject as context. | High |
| FR-08-03 | The AI response shall be structured as: Overview, Key Concepts, Important Formulas (if applicable), Common Mistakes, and NEET Relevance. | High |
| FR-08-04 | The generated explanation shall be rendered with proper formatting (headings, bullet points, bold text). | High |
| FR-08-05 | The system shall cache the AI explanation per topic to avoid redundant API calls (cached for 24 hours). | Medium |
| FR-08-06 | A student shall be able to regenerate the explanation if they want a fresh response. | Low |
| FR-08-07 | The system shall handle API failures gracefully with an appropriate error message. | High |

---

### FR-09: Performance Analytics

**Module Purpose:** Provide deep, visual insights into a student's performance across subjects, chapters, topics, and time.

| ID | Requirement | Priority |
|---|---|---|
| FR-09-01 | The analytics page shall display an overall accuracy trend graph over the last 30 days (line chart). | High |
| FR-09-02 | The analytics page shall display subject-wise accuracy in a radar/spider chart. | High |
| FR-09-03 | The analytics page shall display a chapter-wise accuracy breakdown table, sortable by accuracy. | High |
| FR-09-04 | The analytics page shall display a difficulty-wise performance breakdown (Easy / Medium / Hard). | High |
| FR-09-05 | The analytics page shall display total time spent on the platform per week (bar chart). | Medium |
| FR-09-06 | The analytics page shall display the student's score progression across mock tests (line chart). | High |
| FR-09-07 | The system shall allow filtering analytics by subject and date range. | Medium |
| FR-09-08 | The analytics page shall highlight the student's strongest and weakest chapters. | High |

---

### FR-10: Weak Area Detection (ML)

**Module Purpose:** Use a trained machine learning model to intelligently identify a student's weak topics and recommend targeted practice.

| ID | Requirement | Priority |
|---|---|---|
| FR-10-01 | The system shall train an ML model using student performance data: topic, accuracy, attempt count, difficulty distribution, and time taken. | High |
| FR-10-02 | The model shall classify topics into three categories: Strong, Moderate, Weak. | High |
| FR-10-03 | The system shall update weak area predictions after every practice session or mock test completion. | High |
| FR-10-04 | The top 5 weakest topics per subject shall be surfaced on the dashboard and analytics page. | High |
| FR-10-05 | The system shall recommend the next best topic to practice based on the ML model output. | High |
| FR-10-06 | The ML model shall be built using Scikit-Learn and serialized using Joblib for serving. | High |
| FR-10-07 | The system shall fall back to rule-based weak area detection (accuracy < 50%) if the ML model is unavailable. | Medium |

---

### FR-11: Study Planner

**Module Purpose:** Allow students to create, manage, and track a personal study schedule.

| ID | Requirement | Priority |
|---|---|---|
| FR-11-01 | A student shall be able to create a study plan by selecting topics and assigning a target completion date. | Medium |
| FR-11-02 | The study planner shall display a calendar-style view of scheduled topics. | Medium |
| FR-11-03 | The system shall automatically mark a topic as "Completed" in the planner once the student achieves ≥ 80% accuracy in that topic's practice. | Medium |
| FR-11-04 | The system shall display progress percentage for the overall study plan. | Medium |
| FR-11-05 | A student shall be able to edit or delete study plan entries. | Low |

---

### FR-12: Admin Panel

**Module Purpose:** Provide platform administrators with full control over content, users, and platform health.

| ID | Requirement | Priority |
|---|---|---|
| FR-12-01 | The admin panel shall be accessible only to users with Administrator role. | High |
| FR-12-02 | Administrators shall be able to view, search, filter, activate, and deactivate student accounts. | High |
| FR-12-03 | Administrators shall be able to manage (CRUD) subjects, chapters, topics, and questions. | High |
| FR-12-04 | Administrators shall be able to bulk upload questions via a structured CSV template. | Medium |
| FR-12-05 | Administrators shall be able to view platform usage statistics: total users, daily active users, questions attempted today. | Medium |
| FR-12-06 | Administrators shall be able to view and resolve question reports submitted by students. | Medium |
| FR-12-07 | The admin panel shall extend Django's built-in admin interface with custom views. | High |

---

### FR-13: Notifications

**Module Purpose:** Keep students informed about their activity, milestones, and platform updates.

| ID | Requirement | Priority |
|---|---|---|
| FR-13-01 | The system shall send an in-app notification when a student achieves a new milestone (e.g., 100 questions attempted, 7-day streak). | Medium |
| FR-13-02 | The system shall send an in-app notification when a new mock test is available. | Low |
| FR-13-03 | The system shall display unread notification count in the navigation bar. | Medium |
| FR-13-04 | A student shall be able to view all notifications on a dedicated notifications page. | Medium |
| FR-13-05 | A student shall be able to mark notifications as read individually or all at once. | Low |

---

### FR-14: Leaderboard

**Module Purpose:** Foster healthy competition by ranking students based on their performance metrics.

| ID | Requirement | Priority |
|---|---|---|
| FR-14-01 | The system shall maintain a global leaderboard ranking students by their overall accuracy score and questions attempted (weighted). | Medium |
| FR-14-02 | The leaderboard shall display rank, student name, accuracy percentage, and questions attempted. | Medium |
| FR-14-03 | The leaderboard shall update in real time (or on page load with fresh data). | Medium |
| FR-14-04 | A student shall be able to view their own rank and percentile on the leaderboard page. | Medium |
| FR-14-05 | The leaderboard shall be filterable by subject (Overall, Physics, Chemistry, Biology). | Low |

---

## 5. Requirement Traceability Matrix (RTM)

This matrix maps each module to its priority distribution. It will be expanded during the testing phase to include test case references.

| Module | Total Requirements | High Priority | Medium Priority | Low Priority |
|---|---|---|---|---|
| FR-01: Authentication | 12 | 8 | 3 | 1 |
| FR-02: Dashboard | 10 | 5 | 4 | 1 |
| FR-03: Subject/Topic Mgmt | 8 | 7 | 1 | 0 |
| FR-04: Question Bank | 8 | 5 | 2 | 1 |
| FR-05: Adaptive Practice | 11 | 7 | 3 | 1 |
| FR-06: Mock Test | 10 | 8 | 2 | 0 |
| FR-07: AI Doubt Solver | 10 | 6 | 3 | 1 |
| FR-08: AI Concept Explainer | 7 | 5 | 1 | 1 |
| FR-09: Performance Analytics | 8 | 6 | 2 | 0 |
| FR-10: Weak Area Detection | 7 | 6 | 1 | 0 |
| FR-11: Study Planner | 5 | 0 | 4 | 1 |
| FR-12: Admin Panel | 7 | 4 | 3 | 0 |
| FR-13: Notifications | 5 | 0 | 3 | 2 |
| FR-14: Leaderboard | 5 | 0 | 4 | 1 |
| **TOTAL** | **113** | **67** | **36** | **10** |

---

## Document Control

| Field | Value |
|---|---|
| Document ID | CC-FRD-01 |
| Version | 1.0 |
| Created | 2026-07-29 |
| Last Updated | 2026-07-29 |
| Status | Draft |
| Next Review | Upon team approval |
| Storage Location | `docs/requirements/01_functional_requirements.md` |

---

*End of Document — ConceptCode Functional Requirements v1.0*
