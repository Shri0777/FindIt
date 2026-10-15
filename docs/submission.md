# FindIt — Student Coding Challenge Submission Document

## 1. Project Title
**FindIt — Campus Lost & Found Portal**

---

## 2. Problem Statement
On university and college campuses, lost and found services are fragmented across campus police stations, departmental front desks, libraries, dining halls, and student centers. Students who misplace valuable or essential items (such as keys, student IDs, laptops, chargers, or textbooks) lack a unified, timely way to check if an item was located. Similarly, individuals who find items have no straightforward channel to report them without submitting to physical bureaucracy. This fragmentation leads to low recovery rates, unnecessary replacement costs, and lost study time.

---

## 3. Proposed Solution
**FindIt** is a clean, centralized, web-based Lost & Found bulletin portal designed specifically for campus communities. It provides an open, accessible digital board where students, faculty, and staff can:
- Instantly post lost belongings or items found around campus with location and optional photos.
- Browse chronological listings of reported items.
- Search and filter items simultaneously by keywords, report type (`Lost` vs `Found`), and categories.
- Inspect full item details, review photos, and coordinate retrieval via optional contact info.
- Mark items as returned to their owners once recovered.

---

## 4. Objectives
- **Simplicity and Usability**: Prioritize an intuitive, clutter-free user experience suitable for mobile phones, tablets, and desktops.
- **Reliable Architecture**: Employ a standard Django Model-View-Template (MVT) monolithic design backed by SQLite for zero-configuration, robust local execution.
- **Safety and Input Hygiene**: Enforce strict server-side validation, cross-site request forgery (CSRF) protection, and deep image verification (Pillow content inspection and size limits).
- **Code Readability**: Clean, PEP 8-compliant Python code with thorough docstrings, standard templates, and maintainable CSS without external CDN dependencies.

---

## 5. Implemented Features
1. **Item Reporting**:
   - Web form to submit reports for `Lost` or `Found` belongings.
   - Required fields: title, report type, category, detailed description, campus location, and event date.
   - Server-side date validation rejecting future dates.
   - Optional contact information field.
2. **Optional Image Uploads**:
   - Optional photograph attachment (JPEG, PNG, WebP, GIF).
   - Strict 5 MB maximum file size enforcement.
   - Deep image integrity validation using Pillow (`Image.open().verify()`) preventing malicious file spoofing.
   - Responsive thumbnail display on cards and full-resolution view on the detail page with graceful fallback placeholders.
3. **Browse & Multi-Criteria Filtering**:
   - Chronological grid layout of item cards ordered by newest first.
   - Case-insensitive keyword search (`?q=`) querying both title and description fields via Django ORM `Q` objects.
   - Filter by report type: `All`, `Lost`, `Found`.
   - Filter by category: `Electronics`, `ID & Cards`, `Keys`, `Books & Notebooks`, `Clothing & Accessories`, `Bags & Backpacks`, `Other`.
   - Combined search and filters preserving active selections in URL query parameters.
   - Active filter pill badges with a single-click "Clear all" action.
4. **Item Details & Lifecycle Management ("Mark as Returned")**:
   - Dedicated detail page (`/items/<id>/`) displaying metadata, high-resolution photo, and status.
   - Action form to transition active items to `Returned`.
   - Strict POST-only execution (`@require_POST`) with CSRF protection (GET requests return HTTP 405).
   - Idempotent execution preventing crashes on already-returned items.
   - Auto-updating modification timestamp (`updated_at`).
5. **Real-time Reliable Statistics**:
   - Statistics bar on the browse page computing real-time counts for Total Reports, Active/Open items, and Returned items directly from the database.
6. **Accessible & Responsive Interface**:
   - Fully responsive layout adapting across mobile (320px+), tablet, and desktop viewports.
   - Accessible keyboard focus states (`:focus-visible`), readable color contrast, and reduced-motion support.

---

## 6. Technology Stack
- **Backend Language**: Python 3.10+ (tested on Python 3.14.7)
- **Web Framework**: Django 5.2 (LTS)
- **Database**: SQLite 3 (file-based local persistence)
- **Image Processing**: Pillow (Python Imaging Library)
- **Frontend**: Django Template Language, Semantic HTML5, CSS3, minimal Vanilla JavaScript
- **Testing**: Django Test Framework (`django.test.TestCase`, `Client`)

---

## 7. Architecture Overview
FindIt utilizes Django's monolithic Model-View-Template pattern:
- **`config/`**: Root project configuration containing `settings.py` (database, installed apps, static/media paths) and `urls.py` (root URL dispatcher and development media router).
- **`items/`**: Dedicated domain application:
  - `models.py`: Persistent `Item` data model and choice enums.
  - `forms.py`: `ItemForm` with custom validators for future dates and 5 MB image uploads.
  - `views.py`: Request handlers (`item_list`, `item_create`, `item_detail`, `mark_returned`).
  - `urls.py`: Namespaced routing (`items:item_list`, `items:item_create`, `items:item_detail`, `items:mark_returned`).
  - `tests.py`: Comprehensive test suite.
- **`templates/`**: Global base template (`base.html`) and application templates (`templates/items/`).
- **`static/css/`**: Pure CSS stylesheet (`style.css`) using CSS custom properties (variables) with zero CDN dependencies.
- **`media/`**: Runtime storage directory for user-uploaded photographs (`media/items/%Y/%m/`), excluded from Git tracking.

---

## 8. Database Design Summary
The application persists data in a single SQLite table managed via Django ORM:

| Field Name | Type | Constraints / Rules | Description |
|---|---|---|---|
| `id` | `BigAutoField` | Primary Key, Auto Increment | Unique record identifier |
| `title` | `CharField(100)` | Required, max 100 chars | Descriptive item title |
| `item_type` | `CharField(10)` | Choices: `LOST`, `FOUND`; default `LOST` | Report type |
| `category` | `CharField(20)` | Choices: `ELECTRONICS`, `IDENTIFICATION`, `KEYS`, `BOOKS`, `CLOTHING`, `BAGS`, `OTHER` | Item classification |
| `description` | `TextField` | Required | Comprehensive description |
| `location` | `CharField(150)` | Required, max 150 chars | Campus building or landmark |
| `date_lost_or_found` | `DateField` | Required, `date <= today` | Date item was lost or discovered |
| `contact_info` | `CharField(100)` | Optional (`blank=True`, default `""`) | Email or phone number |
| `status` | `CharField(10)` | Choices: `OPEN`, `RETURNED`; default `OPEN` | Current resolution state |
| `image` | `ImageField` | Optional (`blank=True`, `null=True`, max 5 MB) | Path to uploaded image |
| `created_at` | `DateTimeField` | `auto_now_add=True` | Timestamp when report was filed |
| `updated_at` | `DateTimeField` | `auto_now=True` | Timestamp of last status change |

---

## 9. Testing Summary
FindIt features a comprehensive automated test suite implemented in [`items/tests.py`](file:///home/shri/Development/FindIt/items/tests.py):

- **Total Tests Executed**: 38 automated test cases
- **Pass Rate**: 100% (0 errors, 0 failures)
- **Execution Time**: ~1.0 second
- **Coverage Areas**:
  - `ItemModelTests` (2 tests): Model creation with default status (`OPEN`), string representations, and ordering.
  - `ItemFormTests` (5 tests): Required field validation, optional field handling, future date rejection, and client status injection prevention.
  - `ItemViewTests` (9 tests): Listing views, zero-item empty states, live stats calculations, GET/POST creation flows, invalid input handling, detail view rendering, optional contact info safety, and 404 responses.
  - `SearchAndFilterTests` (10 tests): Title search, description search, case-insensitivity, empty query tolerance, type filters, category filters, combined multi-filters, invalid filter resilience, input preservation, and empty search states.
  - `ReturnedStatusActionTests` (5 tests): POST status transition to `RETURNED`, automatic timestamp updates, GET method rejection (HTTP 405), repeated action idempotency, and record isolation.
  - `ImageUploadTests` (7 tests): Report without photo, valid image upload and storage, oversized upload rejection (>5MB), corrupted file rejection, detail page photo rendering, fallback thumbnails, and temporary media isolation.

---

## 10. Limitations
1. **No User Authentication**: As specified by the project constraints, FindIt operates on an open-campus model without user registration or login. Consequently, the "Mark as Returned" action is open to any visitor for demonstration and grading purposes.
2. **Local Academic Prototype**: The application is configured for local evaluation with `DEBUG = True` and Django's built-in development media serving. It is not hardened for production internet deployment.
3. **Single Database Node**: Relies on SQLite, which is ideal for single-server local evaluation but not intended for distributed multi-instance deployment.

---

## 11. Conclusion
FindIt successfully fulfills all requirements of the four-phase challenge. The resulting codebase is clean, well-tested, robustly validated, visually cohesive, and ready for immediate demonstration and evaluation.
