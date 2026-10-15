# FindIt — Architectural & Technical Design Document

## 1. System Architecture Overview

FindIt is built upon Django's robust Model-View-Template (MVT) pattern, tailored for a clean, monolithic, server-side rendered application without unnecessary micro-abstractions or frontend build toolchains.

```
+-------------------------------------------------------------+
|                         Browser Client                      |
|            (HTML5 semantic markup, CSS3, Vanilla JS)        |
+------------------------------+------------------------------+
                               |
                        HTTP / HTTPS
                               |
+------------------------------v------------------------------+
|                    Django Web Server Layer                  |
|  - config/urls.py (Root Routing & Static/Media Serving)     |
|  - Middleware (Security, CSRF, Clickjacking, Messages)      |
+------------------------------+------------------------------+
                               |
+------------------------------v------------------------------+
|                     items/ Application                      |
|  +-------------------+  +------------------+  +-----------+ |
|  | items/views.py    |  | items/forms.py   |  | templates | |
|  | - item_list       |  | - ItemForm       |  | - base    | |
|  | - item_detail     |  | - Image & Date   |  | - list    | |
|  | - item_create     |  |   Validation     |  | - detail  | |
|  | - mark_returned   |  +------------------+  | - form    | |
|  +---------+---------+                        +-----+-----+ |
|            |                                        |       |
|  +---------v---------+                              |       |
|  | items/models.py   |                              |       |
|  | - Item Model      |                              |       |
|  | - Choices Enums   |                              |       |
|  +---------+---------+                              |       |
+------------|----------------------------------------|-------+
             |                                        |
+------------v-----------+              +-------------v-------+
|  SQLite Database       |              | File System         |
|  (db.sqlite3 via ORM)  |              | (media/items/)      |
+------------------------+              +---------------------+
```

---

## 2. Component Responsibilities

### `config/` (Project Configuration)
- **`settings.py`**: Global settings including database connection (SQLite), registered applications (`items`), template directory resolution, static assets configuration (`STATIC_URL`, `STATICFILES_DIRS`), and runtime media upload configuration (`MEDIA_URL`, `MEDIA_ROOT`).
- **`urls.py`**: Root URL routing delegation to `items.urls` and development media asset serving using `django.conf.urls.static.static`.
- **`wsgi.py` / `asgi.py`**: Standard WSGI/ASGI entrypoints for deployment or local execution.

### `items/` (Core Application)
- **`models.py`**: Encapsulates data persistence for lost and found reports.
- **`forms.py`**: Handles form rendering, request data binding, and comprehensive server-side field and cross-field validation.
- **`views.py`**: View functions processing incoming HTTP requests, orchestrating database queries via Django ORM, and rendering HTML templates.
- **`urls.py`**: Application-specific URL patterns with descriptive route names.

### `templates/` & `static/`
- **`templates/base.html`**: Master layout with metadata, navbar, alerts/messages container, main content block, and footer.
- **`templates/items/`**: Feature templates (`item_list.html`, `item_detail.html`, `item_form.html`).
- **`static/css/style.css`**: CSS styling utilizing custom properties (variables), responsive flexbox and CSS grid layouts, and clean typographic hierarchy.

---

## 3. Data Model Design: `Item`

The `Item` model represents a single lost or found report stored in SQLite.

```python
class Item(models.Model):
    # Enums / Choices
    class ItemType(models.TextChoices):
        LOST = 'LOST', 'Lost'
        FOUND = 'FOUND', 'Found'

    class Category(models.TextChoices):
        ELECTRONICS = 'ELECTRONICS', 'Electronics'
        IDENTIFICATION = 'IDENTIFICATION', 'ID & Cards'
        KEYS = 'KEYS', 'Keys'
        BOOKS = 'BOOKS', 'Books & Notebooks'
        CLOTHING = 'CLOTHING', 'Clothing & Accessories'
        BAGS = 'BAGS', 'Bags & Backpacks'
        OTHER = 'OTHER', 'Other'

    class Status(models.TextChoices):
        OPEN = 'OPEN', 'Open'
        RETURNED = 'RETURNED', 'Returned'

    # Core Fields
    title = models.CharField(max_length=100, help_text="Short title describing the item")
    item_type = models.CharField(max_length=10, choices=ItemType.choices, default=ItemType.LOST)
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.OTHER)
    description = models.TextField(help_text="Detailed description of the item")
    location = models.CharField(max_length=150, help_text="Campus location where lost or found")
    date_lost_or_found = models.DateField(help_text="Date when the item was lost or found")
    contact_info = models.CharField(max_length=100, blank=True, default='', help_text="Optional contact email or phone number")
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.OPEN)
    image = models.ImageField(upload_to='items/%Y/%m/', blank=True, null=True, help_text="Optional photograph")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.get_item_type_display()}] {self.title}"
```

---

## 4. URL Routing & View Design

| URL Pattern | View Name | Method | Responsibility | Status |
|---|---|---|---|---|
| `/` | `items:item_list` | `GET` | Home & listing page. Displays items chronologically with keyword search (`?q=`), type filter (`?type=`), and category filter (`?category=`), with active filter pills and empty states. | **Implemented (Phase 3)** |
| `/items/new/` | `items:item_create` | `GET`, `POST` | Renders report submission form (GET) and processes new report creation with validation, optional image uploads, and messages (POST). | **Implemented (Phase 3)** |
| `/items/<int:pk>/` | `items:item_detail` | `GET` | Shows comprehensive details of an item by primary key; returns 404 if missing; displays uploaded photo and Mark as Returned action. | **Implemented (Phase 3)** |
| `/items/<int:pk>/return/` | `items:mark_returned` | `POST` | Safe state transition marking an OPEN item as RETURNED. Guarded with `@require_POST` and CSRF protection. Updates `status` and `updated_at`. | **Implemented (Phase 3)** |

---

## 5. Forms, Validation, and Processing

### Form Processing (`forms.py`)
- Subclasses `forms.ModelForm` bound to `Item` fields (`title`, `item_type`, `category`, `description`, `location`, `date_lost_or_found`, `contact_info`, `image`).
- `status`, `created_at`, and `updated_at` are excluded from the form, preventing arbitrary client overrides.
- Native HTML5 widgets and accessible labels configured.
- Server-side validation rules:
  1. **Date Validation**: Ensures `date_lost_or_found <= timezone.localdate()`. Submissions with future dates are blocked with an explicit error: *"Date cannot be in the future."*
  2. **Required Fields**: `title`, `item_type`, `category`, `description`, `location`, `date_lost_or_found` are strictly validated on the server.
  3. **Optional Contact Info**: `contact_info` is optional (`blank=True`).
  4. **Image Upload Validation**: Enforces maximum file size of 5 MB and verifies file integrity and format (JPEG, PNG, WebP, GIF) via Pillow.

### Search and Filtering Pipeline (`views.py`)
- Handled dynamically inside `item_list` using standard GET parameters (`q`, `type`, `category`):
  ```python
  queryset = Item.objects.all().order_by('-created_at')
  q = request.GET.get('q', '').strip()
  if q:
      queryset = queryset.filter(Q(title__icontains=q) | Q(description__icontains=q))

  item_type = request.GET.get('type', '').strip()
  if item_type in Item.ItemType.values:
      queryset = queryset.filter(item_type=item_type)

  category = request.GET.get('category', '').strip()
  if category in Item.Category.values:
      queryset = queryset.filter(category=category)
  ```
- Unrecognized or invalid filter parameters are safely ignored without raising 500 errors.
- Active filters and search queries are preserved and reflected in the UI with single-click clear options.

### Status Transition Workflow (`mark_returned`)
- HTTP POST-only endpoint (`@require_POST`).
- Rejects GET requests with HTTP 405 Method Not Allowed.
- Atomically transitions `item.status` from `OPEN` to `RETURNED`, automatically updating `updated_at`.
- Repeated submissions or already-returned items are handled idempotently without error.

---

## 6. Media Handling & Upload Safety

1. **Storage Structure**: Files stored under `media/items/%Y/%m/` organized chronologically.
2. **File Size Enforcement**: 5 MB maximum limit checked on the server before storage.
3. **MIME & Integrity Validation**: Pillow `Image.open().verify()` inspects the raw byte stream to verify valid image headers and structure, rejecting executable or spoofed files. Allowed formats: JPEG, PNG, WebP, GIF.
4. **Development Serving**: `django.conf.urls.static.static` safely serves uploaded files from `MEDIA_ROOT` when `DEBUG = True`.
5. **Fallback Handling**: Items without an image cleanly render a semantic fallback icon on listing cards and omit the photo section on detail views.
6. **Repository Safety**: `.gitignore` configured to exclude user media while preserving directory structure.

---

## 7. User Interface, Navigation & Responsive Layout

### Layout Strategy
- **Base Container**: Semantic `<header>`, `<main>`, and `<footer>` components.
- **Header & Navigation**:
  - Brand identity ("FindIt") linking to root `/`.
  - Primary call-to-action button: "+ Report Item" (`/items/new/`).
  - Filter and search bar with intuitive select dropdowns and search inputs.
- **Card Grid**: CSS Grid (`grid-template-columns: repeat(auto-fill, minmax(280px, 1fr))`) ensuring auto-flow on mobile (single column) through wide desktop (up to 4 columns).
- **Detail View**: 2-column layout on desktop (photo on left, metadata and actions on right), collapsing into a vertical stack on mobile.
- **UI States**:
  - Badge colors: Green for `Found`, Amber/Coral for `Lost`, Slate for `Returned`.
  - Empty state with illustration/icon and helpful reset buttons when searches return 0 items.

---

## 8. Security & Error Handling Considerations

1. **CSRF Protection**: All state-modifying requests (`POST` to `/items/new/` and `/items/<pk>/return/`) are strictly protected with Django's `{% csrf_token %}` middleware.
2. **SQL Injection Defense**: Rely 100% on Django ORM parameterized queries (`filter`, `Q`).
3. **Cross-Site Scripting (XSS)**: Rely on Django's auto-escaping in templates; user-submitted strings are escaped by default.
4. **404 / 500 Handling**: Use `get_object_or_404` for detail and action views to handle non-existent IDs gracefully.
5. **Form Error Feedback**: Display field-level error messages alongside input widgets and global form errors in an alert box.
