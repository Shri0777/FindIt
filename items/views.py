from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import ItemForm
from .models import Item


def item_list(request):
    """
    Displays lost and found reports ordered newest first, with support for
    keyword search and type/category filters.
    """
    q = request.GET.get('q', '').strip()
    item_type = request.GET.get('type', '').strip()
    category = request.GET.get('category', '').strip()

    queryset = Item.objects.all().order_by('-created_at')

    # Apply search query across title and description
    if q:
        queryset = queryset.filter(Q(title__icontains=q) | Q(description__icontains=q))

    # Apply type filter if valid choice provided
    valid_type = item_type if item_type in Item.ItemType.values else ''
    if valid_type:
        queryset = queryset.filter(item_type=valid_type)

    # Apply category filter if valid choice provided
    valid_category = category if category in Item.Category.values else ''
    if valid_category:
        queryset = queryset.filter(category=valid_category)

    is_filtered = bool(q or valid_type or valid_category)

    total_count = Item.objects.count()
    open_count = Item.objects.filter(status=Item.Status.OPEN).count()
    returned_count = Item.objects.filter(status=Item.Status.RETURNED).count()

    context = {
        'items': queryset,
        'q': q,
        'selected_type': valid_type,
        'selected_category': valid_category,
        'type_choices': Item.ItemType.choices,
        'category_choices': Item.Category.choices,
        'is_filtered': is_filtered,
        'total_count': total_count,
        'open_count': open_count,
        'returned_count': returned_count,
    }
    return render(request, 'items/item_list.html', context)


def item_create(request):
    """
    Handles submission of a new lost or found item report, including optional photo upload.
    """
    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save()
            messages.success(request, f'Report for "{item.title}" was submitted successfully!')
            return redirect('items:item_detail', pk=item.pk)
    else:
        form = ItemForm()

    return render(request, 'items/item_form.html', {'form': form})


def item_detail(request, pk):
    """
    Displays detailed information for a single lost or found report.
    """
    item = get_object_or_404(Item, pk=pk)
    return render(request, 'items/item_detail.html', {'item': item})


@require_POST
def mark_returned(request, pk):
    """
    Marks an item report as returned to its owner.
    Guarded to accept only POST requests with CSRF protection.
    """
    item = get_object_or_404(Item, pk=pk)

    if item.status == Item.Status.RETURNED:
        messages.info(request, f'"{item.title}" is already marked as returned.')
    else:
        item.status = Item.Status.RETURNED
        item.save(update_fields=['status', 'updated_at'])
        messages.success(request, f'"{item.title}" has been marked as returned to its owner.')

    return redirect('items:item_detail', pk=item.pk)
