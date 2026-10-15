import io
import shutil
import tempfile
from datetime import timedelta
from PIL import Image as PILImage

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from .forms import ItemForm
from .models import Item


def create_test_image(filename="test.png", format="PNG", size=(100, 100), color="blue"):
    file_obj = io.BytesIO()
    image = PILImage.new("RGB", size=size, color=color)
    image.save(file_obj, format=format)
    file_obj.seek(0)
    return SimpleUploadedFile(
        filename,
        file_obj.read(),
        content_type=f"image/{format.lower()}",
    )


class ItemModelTests(TestCase):
    def test_create_item_with_defaults(self):
        item = Item.objects.create(
            title="Keys on blue lanyard",
            item_type=Item.ItemType.LOST,
            category=Item.Category.KEYS,
            description="Set of three keys with a dorm key and a blue lanyard.",
            location="Library 1st floor",
            date_lost_or_found=timezone.localdate(),
        )
        self.assertEqual(item.status, Item.Status.OPEN)
        self.assertEqual(item.contact_info, "")
        self.assertIsNone(item.image.name)
        self.assertIsNotNone(item.created_at)
        self.assertIsNotNone(item.updated_at)
        self.assertEqual(str(item), "[Lost] Keys on blue lanyard")

    def test_ordering_is_newest_first(self):
        item1 = Item.objects.create(
            title="First Item",
            item_type=Item.ItemType.LOST,
            category=Item.Category.OTHER,
            description="First description",
            location="Cafeteria",
            date_lost_or_found=timezone.localdate(),
        )
        item2 = Item.objects.create(
            title="Second Item",
            item_type=Item.ItemType.FOUND,
            category=Item.Category.ELECTRONICS,
            description="Second description",
            location="Student Union",
            date_lost_or_found=timezone.localdate(),
        )
        items = list(Item.objects.all())
        self.assertEqual(items[0], item2)
        self.assertEqual(items[1], item1)


class ItemFormTests(TestCase):
    def test_valid_form(self):
        form_data = {
            'title': 'MacBook Charger',
            'item_type': Item.ItemType.FOUND,
            'category': Item.Category.ELECTRONICS,
            'description': 'White 67W USB-C power adapter found under table 4.',
            'location': 'Library 3rd floor',
            'date_lost_or_found': timezone.localdate(),
            'contact_info': 'finder@campus.edu',
        }
        form = ItemForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_optional_contact_info(self):
        form_data = {
            'title': 'Calculus Textbook',
            'item_type': Item.ItemType.LOST,
            'category': Item.Category.BOOKS,
            'description': 'Stewart Calculus 8th Edition with notes inside.',
            'location': 'Math Building Rm 202',
            'date_lost_or_found': timezone.localdate(),
            'contact_info': '',
        }
        form = ItemForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_missing_required_fields(self):
        form = ItemForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
        self.assertIn('item_type', form.errors)
        self.assertIn('category', form.errors)
        self.assertIn('description', form.errors)
        self.assertIn('location', form.errors)
        self.assertIn('date_lost_or_found', form.errors)
        self.assertNotIn('contact_info', form.errors)
        self.assertNotIn('image', form.errors)

    def test_future_date_rejected(self):
        future_date = timezone.localdate() + timedelta(days=2)
        form_data = {
            'title': 'Winter Jacket',
            'item_type': Item.ItemType.LOST,
            'category': Item.Category.CLOTHING,
            'description': 'Black puffer jacket',
            'location': 'Gym lobby',
            'date_lost_or_found': future_date,
            'contact_info': 'student@campus.edu',
        }
        form = ItemForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('date_lost_or_found', form.errors)
        self.assertEqual(form.errors['date_lost_or_found'], ["Date cannot be in the future."])

    def test_status_field_not_in_form(self):
        form = ItemForm()
        self.assertNotIn('status', form.fields)
        self.assertNotIn('created_at', form.fields)
        self.assertNotIn('updated_at', form.fields)


class ItemViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_item_list_empty_state(self):
        response = self.client.get(reverse('items:item_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'items/item_list.html')
        self.assertContains(response, "No Reports Found")
        self.assertContains(response, "There are currently no active lost or found item reports on campus.")

    def test_item_list_with_items(self):
        Item.objects.create(
            title="Blue Hydro Flask",
            item_type=Item.ItemType.LOST,
            category=Item.Category.OTHER,
            description="32oz flask with stickers",
            location="Science Hall",
            date_lost_or_found=timezone.localdate(),
        )
        response = self.client.get(reverse('items:item_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Blue Hydro Flask")
        self.assertContains(response, "Lost")
        self.assertContains(response, "Science Hall")
        self.assertNotContains(response, "No Reports Found")

    def test_item_list_statistics_context(self):
        Item.objects.create(
            title="Open Item 1",
            item_type=Item.ItemType.LOST,
            category=Item.Category.KEYS,
            description="Keys",
            location="Library",
            date_lost_or_found=timezone.localdate(),
            status=Item.Status.OPEN,
        )
        Item.objects.create(
            title="Open Item 2",
            item_type=Item.ItemType.FOUND,
            category=Item.Category.ELECTRONICS,
            description="Charger",
            location="Cafeteria",
            date_lost_or_found=timezone.localdate(),
            status=Item.Status.OPEN,
        )
        Item.objects.create(
            title="Returned Item 1",
            item_type=Item.ItemType.FOUND,
            category=Item.Category.OTHER,
            description="Umbrella",
            location="Student Union",
            date_lost_or_found=timezone.localdate(),
            status=Item.Status.RETURNED,
        )
        response = self.client.get(reverse('items:item_list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_count'], 3)
        self.assertEqual(response.context['open_count'], 2)
        self.assertEqual(response.context['returned_count'], 1)
        self.assertContains(response, "Portal Statistics")
        self.assertContains(response, "Total Reports")

    def test_item_create_get(self):
        response = self.client.get(reverse('items:item_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'items/item_form.html')
        self.assertIsInstance(response.context['form'], ItemForm)

    def test_item_create_post_valid(self):
        data = {
            'title': 'Student ID Card',
            'item_type': Item.ItemType.FOUND,
            'category': Item.Category.IDENTIFICATION,
            'description': 'Found near vending machines in West Hall.',
            'location': 'West Hall Vending Area',
            'date_lost_or_found': timezone.localdate().isoformat(),
            'contact_info': 'desk@campus.edu',
        }
        response = self.client.post(reverse('items:item_create'), data=data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'items/item_detail.html')
        self.assertContains(response, 'was submitted successfully!')
        self.assertContains(response, 'Student ID Card')

        item = Item.objects.get(title='Student ID Card')
        self.assertEqual(item.item_type, Item.ItemType.FOUND)
        self.assertEqual(item.category, Item.Category.IDENTIFICATION)
        self.assertEqual(item.location, 'West Hall Vending Area')
        self.assertEqual(item.status, Item.Status.OPEN)

    def test_item_create_post_invalid_does_not_persist(self):
        initial_count = Item.objects.count()
        data = {
            'title': '',
            'item_type': Item.ItemType.LOST,
            'category': Item.Category.KEYS,
            'description': 'Room 101 key',
            'location': 'Courtyard',
            'date_lost_or_found': timezone.localdate().isoformat(),
        }
        response = self.client.post(reverse('items:item_create'), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'items/item_form.html')
        self.assertEqual(Item.objects.count(), initial_count)
        self.assertContains(response, 'Please enter an item title.')

    def test_item_detail_success(self):
        item = Item.objects.create(
            title="Casio Scientific Calculator",
            item_type=Item.ItemType.FOUND,
            category=Item.Category.ELECTRONICS,
            description="fx-991EX model left on desk.",
            location="Engineering Bldg Rm 104",
            date_lost_or_found=timezone.localdate(),
            contact_info="prof@campus.edu",
        )
        response = self.client.get(reverse('items:item_detail', kwargs={'pk': item.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'items/item_detail.html')
        self.assertContains(response, "Casio Scientific Calculator")
        self.assertContains(response, "Engineering Bldg Rm 104")
        self.assertContains(response, "prof@campus.edu")

    def test_item_detail_optional_contact_info_renders_safely(self):
        item = Item.objects.create(
            title="Black Umbrella",
            item_type=Item.ItemType.FOUND,
            category=Item.Category.OTHER,
            description="Compact umbrella with curved handle.",
            location="Library Entrance",
            date_lost_or_found=timezone.localdate(),
            contact_info="",
        )
        response = self.client.get(reverse('items:item_detail', kwargs={'pk': item.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No contact info provided")

    def test_item_detail_nonexistent_returns_404(self):
        response = self.client.get(reverse('items:item_detail', kwargs={'pk': 99999}))
        self.assertEqual(response.status_code, 404)


class SearchAndFilterTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.item1 = Item.objects.create(
            title="Lost iPhone 13 Pro",
            item_type=Item.ItemType.LOST,
            category=Item.Category.ELECTRONICS,
            description="Midnight blue case, cracked screen protector.",
            location="Library 2nd Floor",
            date_lost_or_found=timezone.localdate(),
        )
        self.item2 = Item.objects.create(
            title="Found Chemistry Textbook",
            item_type=Item.ItemType.FOUND,
            category=Item.Category.BOOKS,
            description="Organic Chemistry 5th ed with lecture notes inside.",
            location="Science Hall Rm 301",
            date_lost_or_found=timezone.localdate(),
        )
        self.item3 = Item.objects.create(
            title="Car Keys with Lanyard",
            item_type=Item.ItemType.LOST,
            category=Item.Category.KEYS,
            description="Honda car key attached to a red university lanyard.",
            location="Student Parking Lot B",
            date_lost_or_found=timezone.localdate(),
        )
        self.item4 = Item.objects.create(
            title="Found Backpack",
            item_type=Item.ItemType.FOUND,
            category=Item.Category.BAGS,
            description="Gray JanSport backpack left behind after lunch.",
            location="Campus Cafeteria",
            date_lost_or_found=timezone.localdate(),
        )

    def test_search_by_title(self):
        response = self.client.get(reverse('items:item_list'), {'q': 'iPhone'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Lost iPhone 13 Pro")
        self.assertNotContains(response, "Chemistry Textbook")
        self.assertNotContains(response, "Car Keys with Lanyard")
        self.assertNotContains(response, "Found Backpack")

    def test_search_by_description(self):
        response = self.client.get(reverse('items:item_list'), {'q': 'Honda'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Car Keys with Lanyard")
        self.assertNotContains(response, "Lost iPhone 13 Pro")

    def test_search_case_insensitive(self):
        response = self.client.get(reverse('items:item_list'), {'q': 'iphone'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Lost iPhone 13 Pro")

    def test_search_whitespace_trimmed_and_empty_query_ignored(self):
        response = self.client.get(reverse('items:item_list'), {'q': '   '})
        self.assertEqual(response.status_code, 200)
        # Empty search string returns all items
        self.assertEqual(len(response.context['items']), 4)

    def test_filter_by_type_lost(self):
        response = self.client.get(reverse('items:item_list'), {'type': 'LOST'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Lost iPhone 13 Pro")
        self.assertContains(response, "Car Keys with Lanyard")
        self.assertNotContains(response, "Chemistry Textbook")
        self.assertNotContains(response, "Found Backpack")

    def test_filter_by_type_found(self):
        response = self.client.get(reverse('items:item_list'), {'type': 'FOUND'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Chemistry Textbook")
        self.assertContains(response, "Found Backpack")
        self.assertNotContains(response, "Lost iPhone 13 Pro")
        self.assertNotContains(response, "Car Keys with Lanyard")

    def test_filter_by_category(self):
        response = self.client.get(reverse('items:item_list'), {'category': 'BOOKS'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Chemistry Textbook")
        self.assertEqual(len(response.context['items']), 1)

    def test_combined_search_and_filters(self):
        response = self.client.get(
            reverse('items:item_list'),
            {'q': 'backpack', 'type': 'FOUND', 'category': 'BAGS'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Found Backpack")
        self.assertEqual(len(response.context['items']), 1)

    def test_empty_search_results_message(self):
        response = self.client.get(reverse('items:item_list'), {'q': 'NonExistentItem12345'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No Matching Reports")
        self.assertContains(response, "Clear All Filters")

    def test_invalid_filter_values_safely_ignored(self):
        response = self.client.get(
            reverse('items:item_list'),
            {'type': 'INVALID_TYPE', 'category': 'FAKE_CATEGORY'}
        )
        self.assertEqual(response.status_code, 200)
        # Invalid choices are gracefully ignored, returning all 4 items
        self.assertEqual(len(response.context['items']), 4)

    def test_search_and_filter_preserves_inputs_in_context(self):
        response = self.client.get(
            reverse('items:item_list'),
            {'q': 'Honda', 'type': 'LOST', 'category': 'KEYS'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['q'], 'Honda')
        self.assertEqual(response.context['selected_type'], 'LOST')
        self.assertEqual(response.context['selected_category'], 'KEYS')
        self.assertTrue(response.context['is_filtered'])


class ReturnedStatusActionTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.item = Item.objects.create(
            title="Dorm Keys",
            item_type=Item.ItemType.LOST,
            category=Item.Category.KEYS,
            description="Room 402 key",
            location="North Quad",
            date_lost_or_found=timezone.localdate(),
            status=Item.Status.OPEN,
        )
        self.other_item = Item.objects.create(
            title="Calculator",
            item_type=Item.ItemType.FOUND,
            category=Item.Category.ELECTRONICS,
            description="TI-84 Plus",
            location="Math Lab",
            date_lost_or_found=timezone.localdate(),
            status=Item.Status.OPEN,
        )

    def test_post_marks_item_as_returned(self):
        original_updated_at = self.item.updated_at
        response = self.client.post(
            reverse('items:mark_returned', kwargs={'pk': self.item.pk}),
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'items/item_detail.html')
        self.assertContains(response, 'has been marked as returned to its owner.')

        self.item.refresh_from_db()
        self.assertEqual(self.item.status, Item.Status.RETURNED)
        self.assertGreaterEqual(self.item.updated_at, original_updated_at)

        # Other item status must be completely untouched
        self.other_item.refresh_from_db()
        self.assertEqual(self.other_item.status, Item.Status.OPEN)

    def test_get_request_cannot_change_status(self):
        # View is guarded by @require_POST -> returns 405 Method Not Allowed
        response = self.client.get(reverse('items:mark_returned', kwargs={'pk': self.item.pk}))
        self.assertEqual(response.status_code, 405)

        self.item.refresh_from_db()
        self.assertEqual(self.item.status, Item.Status.OPEN)

    def test_repeated_action_handled_safely(self):
        self.item.status = Item.Status.RETURNED
        self.item.save()

        response = self.client.post(
            reverse('items:mark_returned', kwargs={'pk': self.item.pk}),
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'is already marked as returned.')

        self.item.refresh_from_db()
        self.assertEqual(self.item.status, Item.Status.RETURNED)

    def test_mark_returned_nonexistent_item_returns_404(self):
        response = self.client.post(reverse('items:mark_returned', kwargs={'pk': 99999}))
        self.assertEqual(response.status_code, 404)


class ImageUploadTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.temp_media = tempfile.mkdtemp()
        cls.override_settings = override_settings(MEDIA_ROOT=cls.temp_media)
        cls.override_settings.enable()

    @classmethod
    def tearDownClass(cls):
        cls.override_settings.disable()
        shutil.rmtree(cls.temp_media, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.client = Client()

    def test_create_item_without_image_remains_valid(self):
        data = {
            'title': 'Blue Scarf',
            'item_type': Item.ItemType.FOUND,
            'category': Item.Category.CLOTHING,
            'description': 'Wool knitted scarf found on bench.',
            'location': 'Campus Green',
            'date_lost_or_found': timezone.localdate().isoformat(),
        }
        response = self.client.post(reverse('items:item_create'), data=data, follow=True)
        self.assertEqual(response.status_code, 200)
        item = Item.objects.get(title='Blue Scarf')
        self.assertFalse(bool(item.image))

    def test_create_item_with_valid_image(self):
        uploaded_image = create_test_image(filename="flask.png", format="PNG")
        data = {
            'title': 'Red Water Bottle',
            'item_type': Item.ItemType.FOUND,
            'category': Item.Category.OTHER,
            'description': 'Insulated stainless steel bottle.',
            'location': 'Gym Entrance',
            'date_lost_or_found': timezone.localdate().isoformat(),
            'image': uploaded_image,
        }
        response = self.client.post(reverse('items:item_create'), data=data, follow=True)
        self.assertEqual(response.status_code, 200)
        item = Item.objects.get(title='Red Water Bottle')
        self.assertTrue(bool(item.image))
        self.assertIn("flask", item.image.name)

    def test_create_item_with_oversized_image_rejected(self):
        import os
        # Valid PNG image whose size exceeds 5 MB
        large_img = PILImage.frombytes('RGB', (1600, 1600), os.urandom(1600 * 1600 * 3))
        f = io.BytesIO()
        large_img.save(f, format='PNG')
        f.seek(0)
        oversized_file = SimpleUploadedFile("big.png", f.read(), content_type="image/png")

        data = {
            'title': 'Huge Image Test',
            'item_type': Item.ItemType.LOST,
            'category': Item.Category.OTHER,
            'description': 'Testing large image rejection',
            'location': 'Library',
            'date_lost_or_found': timezone.localdate().isoformat(),
            'image': oversized_file,
        }
        response = self.client.post(reverse('items:item_create'), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Image file size cannot exceed 5MB.")
        self.assertEqual(Item.objects.filter(title='Huge Image Test').count(), 0)

    def test_create_item_with_invalid_corrupted_image_rejected(self):
        fake_file = SimpleUploadedFile("corrupted.png", b"not-a-real-image-data", content_type="image/png")
        data = {
            'title': 'Corrupted Image Test',
            'item_type': Item.ItemType.LOST,
            'category': Item.Category.OTHER,
            'description': 'Testing corrupted image validation',
            'location': 'Library',
            'date_lost_or_found': timezone.localdate().isoformat(),
            'image': fake_file,
        }
        response = self.client.post(reverse('items:item_create'), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Upload a valid image")
        self.assertEqual(Item.objects.filter(title='Corrupted Image Test').count(), 0)

    def test_item_detail_displays_uploaded_image(self):
        uploaded_image = create_test_image(filename="wallet.png", format="PNG")
        item = Item.objects.create(
            title="Leather Wallet",
            item_type=Item.ItemType.LOST,
            category=Item.Category.OTHER,
            description="Brown leather tri-fold wallet.",
            location="Student Union",
            date_lost_or_found=timezone.localdate(),
            image=uploaded_image,
        )
        response = self.client.get(reverse('items:item_detail', kwargs={'pk': item.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, item.image.url)
        self.assertContains(response, 'Attached Photograph')

    def test_item_detail_without_image_renders_cleanly(self):
        item = Item.objects.create(
            title="Earrings",
            item_type=Item.ItemType.FOUND,
            category=Item.Category.CLOTHING,
            description="Silver hoop earrings.",
            location="Music Hall",
            date_lost_or_found=timezone.localdate(),
        )
        response = self.client.get(reverse('items:item_detail', kwargs={'pk': item.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Attached Photograph')
        self.assertContains(response, 'Earrings')

    def test_item_list_thumbnail_and_placeholder(self):
        uploaded_image = create_test_image(filename="watch.png", format="PNG")
        Item.objects.create(
            title="Smart Watch",
            item_type=Item.ItemType.LOST,
            category=Item.Category.ELECTRONICS,
            description="Black digital watch",
            location="Gym",
            date_lost_or_found=timezone.localdate(),
            image=uploaded_image,
        )
        Item.objects.create(
            title="Water Bottle",
            item_type=Item.ItemType.FOUND,
            category=Item.Category.OTHER,
            description="Green bottle",
            location="Library",
            date_lost_or_found=timezone.localdate(),
        )
        response = self.client.get(reverse('items:item_list'))
        self.assertEqual(response.status_code, 200)
        # Should render image tag for Smart Watch and placeholder for Water Bottle
        self.assertContains(response, 'thumb-img')
        self.assertContains(response, 'card-thumb-placeholder')
