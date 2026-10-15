# FindIt — Requirements Specification

## 1. Project Overview

**FindIt** is a lightweight, responsive campus Lost & Found web portal developed for a student coding challenge. The application provides an open, streamlined system allowing students, faculty, and campus staff to report lost or found belongings, browse active reports, search and filter listings, view item details, and mark items as returned once resolved.

---

## 2. Core Functional Requirements

### A. Report an Item
Users can submit a report for either a lost personal item or an item they discovered on campus.

#### Specifications:
1. **Item Name / Title**:
   - Short, descriptive title (e.g., *"Blue Hydro Flask 32oz"*, *"Keys with Red Lanyard"*).
   - Required; maximum 100 characters.
2. **Report Type**:
   - Distinction between `Lost` (user misplaced an item) and `Found` (user picked up/spotted an item).
   - Required choice; radio buttons or select dropdown.
3. **Category**:
   - Predefined campus-relevant categories (e.g., Electronics, Identification & Cards, Keys, Books & Notebooks, Clothing & Accessories, Bags & Backpacks, Other).
   - Required choice.
4. **Description**:
   - Detailed text specifying condition, distinctive marks, identifiers, or circumstances.
   - Required; multiline text area.
5. **Location**:
   - Campus location where the item was lost or found (e.g., *"Library 2nd Floor, Room 204"*, *"Student Center Cafeteria"*, *"Gym Locker Room"*).
   - Required; maximum 150 characters.
6. **Date Lost or Found**:
   - Date when the incident occurred or when the item was spotted.
   - Required; standard ISO date input (`YYYY-MM-DD`). Cannot be in the future.
7. **Contact Information**:
   - Contact email or phone number for the finder/owner to coordinate retrieval.
   - Required; maximum 100 characters.
8. **Optional Photograph**:
   - Image file upload (JPEG, PNG, WebP) displaying the item.
   - Optional; validated for allowed image types and reasonable file size (<= 5MB).

---

### B. Browse and Inspect Reports
Users can browse all reported items in a clean, visual layout, search by keywords, filter by attributes, and inspect individual reports.

#### Specifications:
1. **Responsive Card Layout**:
   - Grid or card-based overview displaying active items chronologically (newest reports first).
   - Each card displays item thumbnail (or clean placeholder if no image), title, report type badge (`Lost` vs `Found`), category badge, location, date, and status.
2. **Search Functionality**:
   - Keyword query matching against item name and description.
   - Preserves active filters when search is submitted.
3. **Filtering**:
   - Filter by Type: `All`, `Lost`, `Found`.
   - Filter by Category: `All` or specific category.
   - Filter by Status: Active/Unresolved vs Returned/Resolved (or toggled view).
4. **Item Detail View**:
   - Dedicated page showing full item metadata: large photo (if provided), complete description, exact location, date, contact details, current status, and resolution controls.
5. **Empty States**:
   - Informative, user-friendly empty states when no reports exist in the system, or when search/filter criteria yield zero matches, with a quick action to reset filters or report an item.

---

### C. Mark an Item as Returned
Provides a straightforward workflow to resolve an item report once an item has been reclaimed by its owner.

#### Specifications:
1. **Status Transitions**:
   - Two fundamental states: `Active` (unresolved / open) and `Returned` (resolved / returned to owner).
   - Clearly indicated via color-coded badges (`Active` = emerald/green, `Returned` = slate/gray).
2. **Action Trigger**:
   - Detail view provides a single-click action (POST request with CSRF protection) to toggle or mark the item as `Returned`.
3. **Persistence**:
   - Status updates are immediately committed to the SQLite database.
4. **Visual Differentiation**:
   - Returned items display a clear "Returned / Resolved" banner or badge.
   - When viewing listings, returned items can be visually dimmed or filtered to keep active reports prominent.

---

## 3. Non-Functional Requirements & Constraints

1. **No User Accounts / Authentication**:
   - No login, registration, password hashing, or role-based access control. The portal operates on an open-campus model to minimize submission friction.
2. **No External APIs or AI Services**:
   - Self-contained application logic with zero dependency on third-party cloud APIs, external AI vision models, or webhook services.
3. **No Notifications / Messaging Subsystems**:
   - Direct communication is handled via the contact info provided in the report. No transactional mail servers (SMTP), WebSockets, or push notifications.
4. **No Complex Single-Page Application (SPA) Frameworks**:
   - No React, Angular, Vue, Node.js build pipelines, npm, or webpack.
   - Standard Django server-rendered templates with semantic HTML5, modern CSS, and minimal vanilla JavaScript only where necessary for UX enhancements.
5. **Database**:
   - SQLite for zero-configuration, reliable local file-based persistence.
6. **Portability & Local Execution**:
   - Runs cleanly inside a standard Python 3.10+ virtual environment (`.venv`) with minimal dependencies (`Django`, `Pillow`).

---

## 4. Testable Acceptance Criteria & Status

| ID | Feature | Acceptance Criteria | Implementation Status |
|---|---|---|---|
| **AC-01** | Report Submission (Valid) | Given valid form inputs (title, type, category, description, location, date, contact), when submitted, a new `Item` record is created in SQLite and the user is redirected to the item detail page with a success confirmation. | **Implemented (Phase 2)** |
| **AC-02** | Report Submission (Missing Fields) | When required fields (e.g., title, description, location) are omitted, the form is re-rendered with specific field validation error messages and previous inputs preserved. | **Implemented (Phase 2)** |
| **AC-03** | Future Date Validation | When a user enters a date later than today, the form rejects the submission with a clear error: *"Date cannot be in the future"*. | **Implemented (Phase 2)** |
| **AC-04** | Optional Image Upload | When an image is uploaded (PNG/JPG/WebP/GIF <= 5MB), it is stored under `media/items/` and rendered on both listing cards and the detail view. When no image is provided, a clean fallback is rendered. | **Implemented (Phase 3)** |
| **AC-05** | Image Security / MIME Validation | Submitting a non-image file (e.g., `.exe`, `.txt`) or corrupted file disguised as an image is rejected with an invalid image error. | **Implemented (Phase 3)** |
| **AC-06** | Listing Display | The home/browse page lists all items ordered by creation date descending, rendering titles, badges, dates, and locations correctly. | **Implemented (Phase 2)** |
| **AC-07** | Keyword Search | Submitting `?q=wallet` returns only items whose name or description contains the substring "wallet" (case-insensitive). | **Implemented (Phase 3)** |
| **AC-08** | Combined Filtering | Selecting `Type = Lost` and `Category = Electronics` filters the results to match both conditions simultaneously. | **Implemented (Phase 3)** |
| **AC-09** | Empty State Feedback | When no items exist in the database or zero search/filter matches occur, an informative empty state message is shown with a call to action. | **Implemented (Phase 3)** |
| **AC-10** | Status Update (Return) | Triggering the "Mark as Returned" POST action on an active item changes its status to `Returned`, updates the database, and immediately reflects the "Returned" badge on the UI. | **Implemented (Phase 3)** |
| **AC-11** | CSRF Protection | Every state-changing form (item submission, status toggle) includes a valid Django CSRF token; requests lacking a valid token fail with HTTP 403. | **Implemented (Phase 2 & 3)** |
| **AC-12** | Responsive Layout | The interface adapts seamlessly across mobile screens (320px+), tablets, and desktop displays without horizontal overflow or broken cards. | **Implemented (Phase 2 & 3)** |

