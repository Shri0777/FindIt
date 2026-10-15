from django.db import models


class Item(models.Model):
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

    title = models.CharField(
        max_length=100,
        help_text="Short title describing the item",
    )
    item_type = models.CharField(
        max_length=10,
        choices=ItemType.choices,
        default=ItemType.LOST,
        help_text="Whether this item was lost or found",
    )
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.OTHER,
        help_text="Category of the item",
    )
    description = models.TextField(
        help_text="Detailed description of the item",
    )
    location = models.CharField(
        max_length=150,
        help_text="Campus location where lost or found",
    )
    date_lost_or_found = models.DateField(
        help_text="Date when the item was lost or found",
    )
    contact_info = models.CharField(
        max_length=100,
        blank=True,
        default='',
        help_text="Optional contact email or phone number",
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.OPEN,
        help_text="Current report status",
    )
    image = models.ImageField(
        upload_to='items/%Y/%m/',
        blank=True,
        null=True,
        help_text="Optional photograph",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.get_item_type_display()}] {self.title}"
