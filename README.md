# FindIt — Campus Lost & Found Portal

**FindIt** is a clean, lightweight, and responsive web application built with Python and Django. Designed for college and university campuses, it provides an open digital bulletin board where students, faculty, and staff can easily report lost or found belongings, browse listings, filter by categories, coordinate returns, and mark items as resolved.

---

## 1. Problem Statement

On university and college campuses, lost-and-found operations are notoriously fragmented across disparate departmental offices, security desks, library kiosks, and dining halls. Students who misplace items often have no central, timely way to check if an item was located, while finders lack a simple channel to broadcast found belongings without navigating bureaucracy.

**FindIt** solves this by establishing a unified, accessible digital lost-and-found portal where campus members can immediately report items, search across listings, coordinate returns, and mark items as returned to their owners.

---

## 2. Project Objectives

- **High Usability**: Simple, responsive card layout accessible across mobile screens, tablets, and desktops.
- **Robust Architecture**: Built with standard Django Model-View-Template (MVT) patterns and SQLite for zero-configuration, reliable local execution.
- **Data Integrity & Security**: Comprehensive server-side form validation, CSRF protection, and Pillow-based image verification.
- **Zero Overhead**: Zero external frontend framework dependencies, no Node.js or npm toolchains, and no third-party cloud services.

---

## 3. Implemented Features

- **Item Reporting**: Submit reports for `Lost` or `Found` belongings with title, report type, category, description, campus location, date, optional contact info, and optional photograph.
- **Server-Side Validation**:
  - Enforces required fields with understandable error messages.
  - Rejects future dates (`date_lost_or_found > today`).
  - Restricts report types and categories to predefined choices.
  - Excludes server-controlled fields (`status`, timestamps) from client modification.
- **Optional Image Uploads**:
  - Attach photos in JPEG, PNG, WebP, or GIF formats.
  - Server-side 5 MB file size limit enforcement.
  - Deep file integrity inspection using Pillow (`Image.open().verify()`) preventing disguised or corrupted files.
  - Fallback placeholders for reports without photographs.
- **Keyword Search**:
  - Case-insensitive search (`?q=`) matching across both item titles and descriptions.
  - Retains search query in the input field across filter changes.
- **Multi-Criteria Filtering**:
  - Filter by report type: `All`, `Lost`, `Found`.
  - Filter by category: `Electronics`, `ID & Cards`, `Keys`, `Books & Notebooks`, `Clothing & Accessories`, `Bags & Backpacks`, `Other`.
  - Combined search and filters preserving active selections in URL parameters.
  - Active filter pill badges with single-click "Clear all" action.
- **Item Resolution ("Mark as Returned")**:
  - Explicit, CSRF-protected POST action on the item detail page to transition an active report to `Returned`.
  - Automatically updates the modification timestamp (`updated_at`).
  - Idempotent and safe against repeated clicks.
- **Real-Time Database Statistics**:
  - Statistics bar on the browse page reporting exact counts for Total Reports, Active/Open items, and Returned items directly from SQLite records.
- **Contextual Empty States**:
  - Helpful empty states distinguishing between a zero-report database and zero-match search/filter results.
- **Accessibility & Polish**:
  - Visible keyboard focus rings (`:focus-visible`).
  - Respects reduced-motion preferences (`prefers-reduced-motion: reduce`).

---

## 4. Technology Stack

- **Backend**: Python 3.10+ (tested on Python 3.14.7), Django 5.2 (LTS)
- **Frontend**: Django Templates, Semantic HTML5, CSS3, minimal Vanilla JavaScript
- **Database**: SQLite 3 (file-based local persistence)
- **Image Processing**: Pillow (Python Imaging Library)
- **Testing**: Django Test Framework (`django.test.TestCase`, `Client`)

---

## 5. Prerequisites

- **Linux** (or macOS / WSL on Windows)
- **Python 3.10+** (with standard library `venv` and `sqlite3` support)
- **pip** (Python package installer)
- **Git**

---

## 6. Getting Started (Linux)

### 1. Clone or Open the Repository
```bash
cd /path/to/FindIt
```

### 2. Create and Activate a Local Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Apply Database Migrations
```bash
python manage.py migrate
```

### 5. Verify System Configuration
```bash
python manage.py check
```

### 6. Run the Local Development Server
```bash
python manage.py runserver
```
Open your browser and navigate to `http://127.0.0.1:8000/`.

---

## 7. Running Automated Tests

Run the complete test suite:
```bash
python manage.py test
```

### Test Coverage (38 Tests Passing)
- **Model Tests**: Creation with defaults, ordering, string representations.
- **Form Tests**: Required fields, optional fields, future date rejection, field protection.
- **View Tests**: Homepage, creation flow, detail page, live statistics calculation, 404 responses.
- **Search & Filter Tests**: Keyword search (title & description, case-insensitive, empty query), type filtering, category filtering, combined filters, invalid filter tolerance.
- **Status Action Tests**: Valid POST status change, GET rejection (HTTP 405), repeated action idempotency, record isolation.
- **Image Upload Tests**: Optional upload, valid persistence, oversized file rejection (>5MB), corrupted file rejection, detail view photo display, card thumbnails, isolated temporary test media.

---

## 8. Image Upload Behavior & Limits

- **Optional Field**: Reports can be submitted with or without a photograph.
- **Max File Size**: 5 MB (`5 * 1024 * 1024` bytes). Submissions exceeding this limit are rejected with an understandable form error.
- **Allowed Formats**: JPEG, PNG, WebP, GIF.
- **Integrity Inspection**: Files are inspected using Pillow's `verify()` method to validate image structure, preventing arbitrary files disguised as images.
- **Storage Location**: Uploaded files are organized chronologically under `media/items/%Y/%m/` and excluded from Git.

---

## 9. Known Limitations & Security Notes

- **Academic Prototype / No User Authentication**: In accordance with the student coding challenge scope, user registration, authentication, and role-based permissions were intentionally excluded. Consequently, the "Mark as Returned" action is accessible to any visitor for demonstration purposes.
- **Local Development Configuration**: The project runs with `DEBUG = True` and uses Django's development static/media server. It is designed for local evaluation and is not hardened for public production deployment.
- **Single Database Node**: Utilizes SQLite for zero-configuration local execution.

---

## 10. Project Documentation

Additional documentation is available in the `docs/` directory:
- [`docs/requirements.md`](file:///home/shri/Development/FindIt/docs/requirements.md): Functional scope, non-functional constraints, and acceptance criteria.
- [`docs/design.md`](file:///home/shri/Development/FindIt/docs/design.md): System architecture, data model, view responsibilities, and media security.
- [`docs/implementation-plan.md`](file:///home/shri/Development/FindIt/docs/implementation-plan.md): Four-phase implementation roadmap and status tracking.
- [`docs/submission.md`](file:///home/shri/Development/FindIt/docs/submission.md): Formal student coding challenge submission document.
- [`docs/demo-script.md`](file:///home/shri/Development/FindIt/docs/demo-script.md): 60–90 second step-by-step demonstration walkthrough.

---

## 11. Project Status

| Phase | Description | Status |
|---|---|---|
| **Phase 1** | Foundation (Project structure, dependencies, documentation, system check) | **Completed** |
| **Phase 2** | Core Features (Item model, migrations, report form, listing & detail views) | **Completed** |
| **Phase 3** | Completion of Functionality (Search, filters, return workflow, image uploads) | **Completed** |
| **Phase 4** | Finalization (Interface polish, regression testing, submission documentation) | **Completed** |
