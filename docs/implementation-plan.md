# FindIt — Four-Phase Implementation Plan

This document outlines the structured roadmap for developing the **FindIt** campus Lost & Found web portal across four discrete, disciplined phases.

---

## Phase 1 — Foundation
*Status: Completed*

- **Repository inspection**:
  - Verify working directory, git status, system tools, Python interpreter version, and SQLite support.
  - Assess environment constraints and blockers.
- **Django project initialization**:
  - Establish `config/` project layout and `items/` application layout.
  - Configure `manage.py`, directory structure (`templates/`, `static/css/`, `media/`, `docs/`).
- **Environment and dependency setup**:
  - Establish local virtual environment (`.venv`).
  - Configure `requirements.txt` (`Django`, `Pillow`).
  - Configure `.gitignore` for development artifacts, bytecode, SQLite database, and runtime media.
- **Requirements, architecture, and implementation documentation**:
  - Author `docs/requirements.md` covering scope, constraints, and testable acceptance criteria.
  - Author `docs/design.md` detailing architecture, data model, views, URLs, forms, and security.
  - Author `docs/implementation-plan.md` defining the 4-phase project execution plan.
- **Initial configuration checks**:
  - Integrate `items.apps.ItemsConfig` into `config/settings.py`.
  - Configure template and static/media directories in settings.
  - Execute `python manage.py check` to verify zero system configuration errors.

---

## Phase 2 — Core Features
*Status: Completed*

- **Item model and database migrations**:
  - Implement `Item` model with fields for title, type (`Lost`/`Found`), category, description, location, date, contact info, status, timestamps, and optional image.
  - Generate initial Django database migrations (`python manage.py makemigrations items`).
  - Apply database migrations to local SQLite (`python manage.py migrate`).
- **Lost/Found reporting form**:
  - Implement `ItemForm` with server-side validation (including past/present date enforcement).
  - Implement report submission view (`item_create`) handling GET and POST.
  - Build `templates/items/item_form.html` with field error rendering and accessible form controls.
- **Browse and detail pages**:
  - Implement home/listing view (`item_list`) retrieving items from SQLite ordered by date.
  - Implement detail view (`item_detail`) displaying all metadata for a selected item.
  - Build `templates/base.html` shell and initial `templates/items/item_list.html` and `templates/items/item_detail.html`.
- **Persistence and form validation**:
  - Validate database persistence through Django test client or shell.
  - Verify rejection of invalid inputs and preservation of user data on validation errors.

---

## Phase 3 — Completion of Functionality
*Status: Completed*

- **Search and category/type filters**:
  - Implement keyword query filtering against title and description using Django ORM `Q` objects.
  - Implement type filtering (`Lost` vs `Found`).
  - Implement category filtering.
  - Integrate search and filter form into the listing header with state retention in URL query parameters.
- **Returned/resolved status transitions**:
  - Implement `mark_returned` view handling state transitions from `ACTIVE` to `RETURNED`.
  - Ensure CSRF protection on status change POST actions.
  - Render status badges and appropriate visual dimming or indicators for resolved items.
- **Optional image uploads**:
  - Configure `enctype="multipart/form-data"` on the submission form.
  - Enable media file upload handling and saving under `media/items/%Y/%m/`.
  - Render uploaded images in listing thumbnails and full resolution in detail views.
  - Provide fallback visuals when an item has no image.
- **Edge cases and user feedback**:
  - Add friendly empty states for empty search results and empty categories.
  - Implement Django messages framework for flash notifications (e.g., "Report submitted successfully!").

---

## Phase 4 — Finalization
*Status: Completed*

- **Responsive visual polish**:
  - Craft clean, responsive styling in `static/css/style.css` (mobile, tablet, desktop).
  - Polish typographic hierarchy, badge styles, form inputs, button states, and spacing.
- **Automated tests and regression checks**:
  - Author automated test suite in `items/tests.py` covering model creation, form validation, future date rejection, search/filter views, and status toggles.
  - Execute test runner (`python manage.py test`) and ensure 100% pass rate.
- **Security and configuration review**:
  - Audit CSRF tokens, template auto-escaping, and file upload validation.
  - Verify settings hygiene and error handling for 404 responses.
- **README and submission documentation**:
  - Update `README.md` with complete installation, execution, and verification instructions.
  - Review documentation accuracy against the working codebase.
- **Final end-to-end verification**:
  - Conduct full manual or automated walkthrough: report an item, browse items, search, filter, view details, mark as returned, and verify database state.
