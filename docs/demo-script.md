# FindIt — Demonstration Walkthrough Script (60–90 Seconds)

This script outlines a concise, structured demonstration of the **FindIt** Campus Lost & Found Portal for evaluators or video recordings.

---

## 1. Preparation & Setup (Before Recording)

### Step 1: Ensure Dependencies and Database are Ready
Run from the repository root:
```bash
# Activate virtual environment
source .venv/bin/activate

# Apply migrations
python manage.py migrate

# Verify tests pass
python manage.py test
```

### Step 2: Seed Sample Records (Optional but Recommended)
To showcase browsing and filtering immediately, you can populate three sample records using Python shell or manage.py:
```bash
python manage.py shell -c "
from items.models import Item
from django.utils import timezone

Item.objects.all().delete()

Item.objects.create(
    title='Casio fx-991EX Calculator',
    item_type=Item.ItemType.FOUND,
    category=Item.Category.ELECTRONICS,
    description='Black scientific calculator left on table in Engineering Hall Rm 104.',
    location='Engineering Hall Room 104',
    date_lost_or_found=timezone.localdate(),
    contact_info='eng-desk@campus.edu',
    status=Item.Status.OPEN
)

Item.objects.create(
    title='Dorm Room Key with Blue Lanyard',
    item_type=Item.ItemType.LOST,
    category=Item.Category.KEYS,
    description='Single brass dorm room key on a navy blue campus lanyard.',
    location='Library 2nd Floor Quiet Study',
    date_lost_or_found=timezone.localdate(),
    contact_info='student42@campus.edu',
    status=Item.Status.OPEN
)

Item.objects.create(
    title='Hydro Flask Water Bottle',
    item_type=Item.ItemType.LOST,
    category=Item.Category.OTHER,
    description='32oz mint green bottle covered in national park stickers.',
    location='Campus Recreation Center Locker Room',
    date_lost_or_found=timezone.localdate(),
    contact_info='gym@campus.edu',
    status=Item.Status.RETURNED
)
print('Demo seed records ready!')
"
```

### Step 3: Start the Development Server
```bash
python manage.py runserver
```
Open your browser to: `http://127.0.0.1:8000/`.

---

## 2. Demonstration Flow (60–90 Seconds)

| Time | Step | Action & Narration | Screen / UI Focus |
|---|---|---|---|
| **0:00 – 0:12** | **1. Opening the Homepage** | Navigate to `http://127.0.0.1:8000/`.<br>*"FindIt is a centralized campus portal where students and staff can report and recover lost or found items. At the top, the portal statistics bar immediately displays total, active, and returned counts."* | Header branding, statistics bar (`Total: 3`, `Active: 2`, `Returned: 1`). |
| **0:13 – 0:25** | **2. Browsing Existing Reports** | Scroll through the card grid.<br>*"Items are displayed chronologically with clear visual badges for report type (Lost vs Found), category, campus location, and current status."* | Item cards, badges (`Lost` in red/rose, `Found` in emerald, `Open` in green, `Returned` in slate). |
| **0:26 – 0:42** | **3. Searching & Filtering** | 1. In the search box, type `Calculator` and click **Filter**.<br>2. Note the keyword pill and filtered result.<br>3. Change Type to `Lost` and click **Filter** to see combined criteria.<br>4. Click **Clear** to restore all records.<br>*"Search operates case-insensitively across titles and descriptions and combines seamlessly with report type and category filters."* | Filter form, active filter pills, search input retention, and one-click reset. |
| **0:43 – 0:60** | **4. Creating a New Report** | Click **+ Report an Item** in the navigation.<br>Fill out the form:<br>- **Title**: `Student ID Card`<br>- **Type**: `Found`<br>- **Category**: `ID & Cards`<br>- **Location**: `Student Center Dining Hall`<br>- **Date**: Today's date<br>- **Contact**: `dining-staff@campus.edu`<br>- **Description**: `Found near tray return station.`<br>- *(Optional)*: Attach an image file.<br>Click **Submit Report**.<br>*"The form performs server-side validation, rejects future dates, and securely handles optional image uploads up to 5MB."* | Form layout, accessible labels, validation help text, submit button. |
| **1:01 – 1:15** | **5. Viewing Item Details** | Notice the flash confirmation message: *"Report for 'Student ID Card' was submitted successfully!"*<br>Review the detail page with full description, metadata sidebar, and attached photograph.<br>*"The detail page presents comprehensive item metadata and a resolution control box."* | Flash message, metadata list, photograph (if uploaded). |
| **1:16 – 1:30** | **6. Marking Item as Returned** | In the sidebar, click the green **✓ Mark as Returned** button.<br>Observe the page reload with the updated status banner: *"Student ID Card has been marked as returned to its owner."*<br>The badge updates to `Status: Returned`.<br>*"Once the owner reclaims their item, a single CSRF-protected POST request marks the report resolved in SQLite and closes the ticket."* | Action box reload, `Returned` badge update, timestamp update. |

---

## 3. Post-Demo Cleanup
To reset demo items back to a clean state:
```bash
python manage.py shell -c "from items.models import Item; Item.objects.all().delete(); print('Cleaned!')"
```
