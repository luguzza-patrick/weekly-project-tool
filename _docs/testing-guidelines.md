# Testing Guidelines

Guidelines for writing tests in this project. Read this before writing any
tests.

## Running tests
- The whole suite: `uv run pytest`
- One test file: `uv run pytest tests/test_home.py`
- One test: `uv run pytest tests/test_home.py::test_name`

## Layout
- Tests live in the top-level `tests/` directory with the project (they are
  not Django's default in-app `tests.py`).
- File names use the `test_*.py` convention (e.g. `tests/test_home.py`).
- Tests for a given domain (models, views, management commands) go in
  dedicated test files rather than one monolithic file.

## Conventions
- `pytest-django` is the runner; use Django's test client for view tests and
  the ORM/database for model tests.
- Name tests to describe behavior, e.g. `test_home_returns_200` or
  `test_invalid_status_is_rejected`.
- Write a test for each behavior as it is added, and run the whole suite
  (`uv run pytest`) before closing an issue to confirm nothing broke.

## Scope
- Tests are part of every task's acceptance criteria (see `_docs/tasks.md`).
- Keep tests focused on observable behavior, not internal implementation
  details.