# Design System

Guidelines for the UI in this project. Read this before touching anything in
the user interface.

## Approach
- The MVP uses **Bootstrap 5** (loaded via CDN or static assets) for layout,
  forms, and components. No custom CSS framework.
- Reuse Bootstrap's utility and component classes instead of writing custom
  styles.

## Structure
- Share a base template (`base.html`) that loads Bootstrap and sets up the
  page shell (nav, content container) used by both the weekly form and the
  dashboard.
- Keep page-specific markup in each page's own template, extending the base.

## Components
- Use Bootstrap forms classes (`.form-control`, `.form-label`) for all inputs.
- Use Bootstrap badges and buttons consistently for status and actions.
- The status recap uses a fixed mapping for the three simple statuses:

| Status     | Badge color |
|------------|-------------|
| On Track   | success (green) |
| At Risk    | warning (yellow) |
| Blocked    | danger (red) |

- Prefer a responsive grid (`.container`, `.row`, `.col-*`) so the form and
  dashboard read well on typical desktop monitors used for the weekly review.

## Consistency
- Match the existing pages (weekly form, dashboard) when adding new UI.
- Polish-only tasks must not change behavior; confirm existing tests pass.