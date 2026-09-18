# Weekly Project Feedback Tool — Task Backlog

Backlog for the MVP scope in `plan.md`, built with the Option 3 stack
(Django + SQLite/PostgreSQL + Bootstrap).

## Tooling & conventions
- Project uses `uv` for dependencies and `pytest` for tests. See
  `_docs/Agent.md` for the canonical commands (`uv sync` to install,
  `uv run pytest` to run the whole suite).
- Dependencies are declared only in `pyproject.toml`. Do not add one without
  asking.
- Tests live in a top-level `tests/` directory (e.g. `tests/test_home.py`).
  Read `_docs/testing-guidelines.md` before writing tests.
- Work is organized as GitHub issues, one at a time. Read the acceptance
  criteria before starting and before closing an issue. Commit regularly.
  See `_docs/process.md`.

## MVP scope
Tasks sizes target one session. Tasks that others build on are ordered first.
The plan's MVP is "one weekly form → multiple projects → project-level
feedback → simple dashboard." Anything that requires reviewing past weeks or
long-term analysis is out of scope for the MVP.

---

## 1. Set up an empty Django project with a passing test
Goal: Create a working, runnable Django skeleton with a passing smoke test.
Description: Install the toolchain with `uv sync`, scaffold the Django project,
add `pytest`/`pytest-django` to `pyproject.toml`, and add `tests/test_home.py`
which asserts the home or health page responds. Verify the server starts and
`uv run pytest` passes.
Acceptance criteria: `uv sync` succeeds; the project runs; `uv run pytest`
passes; `tests/test_home.py` exists and contains the first passing test; no
dependency was added outside `pyproject.toml`.

## 2. Define core models: users with a role, and projects
Goal: Add the foundational `Project` model and a role for users.
Description: Define a `Project` model (name, description, optional owner) in a
`projects` app, and add a role field to the user so Project Managers are
distinguished from Project Team Members (Django Groups or a simple field,
defaulting to Team Member). Add migrations, register in the admin, and write
model-level tests in `tests/`.
Acceptance criteria: `Project` and the user role exist with migrations; both
are registered in admin; tests cover creating a `Project` and the default
user role; `uv run pytest` passes.

## 3. Define the feedback data model: weekly report and per-project feedback
Goal: Model "one weekly report → per-project feedback" with the simple status enum.
Description: Add a `WeeklyReport` model linking a user to a reporting week, and
a `ProjectFeedback` model with a ForeignKey to the report and project, plus
status (On Track / At Risk / Blocked), completion percentage, completed work,
notes, risks/blockers, and action items. Define the three statuses as Django
`Choices` and validate stored values.
Acceptance criteria: both models exist with migrations; status is constrained to
the three valid values and an invalid status is rejected; tests cover creating a
report, per-project feedback, and status validation; `uv run pytest` passes.

## 4. Build the weekly form showing the user's projects
Goal: Render one form where a user enters feedback for each project they are in.
Description: Add a project-membership join (many-to-many or join model) so a
signed-in user's projects are seeded into the form, and build a Django
form/view/template showing the week header plus editing/saving one
`ProjectFeedback` per involved project.
Acceptance criteria: the form renders the signed-in user's projects; GET shows
the week header and per-project inputs; POST saves feedback and redirects;
tests cover GET rendering and POST saving; `uv run pytest` passes.

## 5. Build the dashboard with status summary
Goal: Show a simple weekly view of all projects and their feedback.
Description: Create a dashboard view/template aggregating all feedback for the
current week: project, status, completion, completed work, risks/blockers,
action items, and who reported, with per-status counts (On Track / At Risk /
Blocked). Simple by design — no trend or week navigation per the MVP scope.
Acceptance criteria: seed feedback renders on the dashboard with correct
per-status counts; a test asserts the aggregated numbers appear; `uv run pytest`
passes.

## 6. Style the form and dashboard with Bootstrap
Goal: Apply a clean, readable Bootstrap layout to the two main pages.
Description: Add Bootstrap (via a CDN or static assets) and base templates so
the weekly form and dashboard are navigable and readable. Polish only, with no
behavior changes. Read `_docs/design-system.md` before touching the UI.
Acceptance criteria: both pages use Bootstrap base templates and are navigable;
existing tests still pass; `uv run pytest` passes.

## 7. Add basic authentication and login flow
Goal: Secure the form and dashboard behind a login.
Description: Enable Django authentication (login/logout, `LoginRequired` on the
form and dashboard) with a simple login template and a role-based default.
Acceptance criteria: unauthenticated users are redirected to login; authenticated
users can access form and dashboard; tests cover both cases; `uv run pytest`
passes.

## 8. Seed realistic demo data
Goal: Provide a management command that fills the app with sample data.
Description: Write a Django management command (e.g. `seed_demo`) creating a few
users, projects, a weekly report, and per-project feedback for a demo week.
Make the internal MVP trial quick to set up and review.
Acceptance criteria: the command runs and creates the expected rows; a test
verifies the created rows; `uv run pytest` passes.