from django.contrib import admin
from .models import Item


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'item_type', 'category', 'location', 'date_lost_or_found', 'status', 'created_at')
    list_filter = ('item_type', 'category', 'status', 'date_lost_or_found')
    search_fields = ('title', 'description', 'location')
    readonly_fields = ('created_at', 'updated_at')
