# Weekly Project Feedback Tool — Task Backlog

Backlog for the MVP scope in `plan.md`, built with the Option 3 stack
(Django + SQLite/PostgreSQL + Bootstrap).

Each task is sized to finish in one session and mostly independent. Tasks
that others build on are ordered first; where a task has a hard dependency,
it is noted inline.

MVP scope note: the plan's MVP is "one weekly form → multiple projects →
project-level feedback → simple dashboard." Anything that requires reviewing
past weeks or long-term analysis is out of scope and deferred to the future
possibilities in `plan.md`.

---

## 1. Set up an empty Django project with a passing test
Goal: Create a working, runnable Django skeleton with a passing smoke test.
Description: Create a virtual environment, install Django, and scaffold the project with `django-admin startproject`. Verify the server starts, the built-in default tests pass, and add a minimal `/health/` view with a test asserting it returns HTTP 200. This baseline every later task builds on.

## 2. Define core models: users with a role, and projects
Goal: Add the foundational `Project` model and a role for users.
Description: Define a `Project` model (name, description, optional owner) in a `projects` app, and add a role field to the user so Project Managers are distinguished from Project Team Members (Django Groups or a simple field, defaulting to Team Member). Add migrations, register in the admin, and write model-level tests. This is where the domain objects referenced by the feedback workflow live.

## 3. Define the feedback data model: weekly report and per-project feedback
Goal: Model "one weekly report → per-project feedback" with the simple status enum.
Description: Add a `WeeklyReport` model linking a user to a reporting week, and a `ProjectFeedback` model with a ForeignKey to the report and project, plus status (On Track / At Risk / Blocked), completion percentage, completed work, notes, risks/blockers, and action items. Define the three statuses as Django `Choices` with a test that an invalid status is rejected. This single session is the whole data core of the MVP.

## 4. Build the weekly form showing the user's projects
Goal: Render one form where a user enters feedback for each project they are in.
Description: Add a project-membership join (many-to-many or join model) so a signed-in user's projects are seeded into the form, and build a Django form/view/template showing the week header plus editing/saving one `ProjectFeedback` per involved project. Write tests for GET rendering and POST saving. This delivers the "one form → drill into each project" workflow.

## 5. Build the dashboard with status summary
Goal: Show a simple weekly view of all projects and their feedback.
Description: Create a dashboard view/template aggregating all feedback for the current week: project, status, completion, completed work, risks/blockers, action items, and who reported, with per-status counts (On Track / At Risk / Blocked). Write a test that seeded feedback appears with the correct aggregated numbers. Simple by design — no trend or week navigation per the MVP scope.

## 6. Style the form and dashboard with Bootstrap
Goal: Apply a clean, readable Bootstrap layout to the two main pages.
Description: Add Bootstrap (via a CDN or static assets) and base templates so the weekly form and dashboard are navigable and readable. This is polish only, with no behavior changes; confirm existing tests still pass.

## 7. Add basic authentication and login flow
Goal: Secure the form and dashboard behind a login.
Description: Enable Django authentication (login/logout, `LoginRequired` on the form and dashboard) with a simple login template and a role-based default. Write tests that unauthenticated users are redirected and authenticated users can access the pages.

## 8. Seed realistic demo data
Goal: Provide a management command that fills the app with sample data.
Description: Write a Django management command (e.g. `seed_demo`) creating a few users, projects, a weekly report, and per-project feedback for a demo week, plus a test that it creates the expected rows. This makes the internal MVP trial quick to set up and review.