# ConceptCode Application Architecture

## 1. Purpose

This document defines the application boundaries and dependency rules
for the ConceptCode Django application.

The purpose is to keep the project modular and prevent business logic
from becoming tightly coupled between Django applications.

---

## 2. High-Level Structure

ConceptCode uses Django as the primary web application framework.

The repository is organized into:

- Django project configuration
- Django applications
- standalone Question Generator
- templates
- static assets
- media
- tests
- documentation

### Django applications

```text
apps/
├── core/
├── accounts/
├── content/
├── practice/
├── mock_tests/
├── ai_tutor/
├── analytics/
├── ml_engine/
├── planner/
└── engagement/