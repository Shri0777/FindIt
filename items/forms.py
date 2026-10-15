from django import forms
from django.utils import timezone
from PIL import Image

from .models import Item


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = [
            'title',
            'item_type',
            'category',
            'description',
            'location',
            'date_lost_or_found',
            'contact_info',
            'image',
        ]
        widgets = {
            'title': forms.TextInput(
                attrs={
                    'class': 'form-input',
                    'placeholder': 'e.g., Blue Hydro Flask 32oz, Keys on red lanyard',
                    'required': True,
                }
            ),
            'item_type': forms.Select(
                attrs={
                    'class': 'form-select',
                    'required': True,
                }
            ),
            'category': forms.Select(
                attrs={
                    'class': 'form-select',
                    'required': True,
                }
            ),
            'description': forms.Textarea(
                attrs={
                    'class': 'form-textarea',
                    'rows': 4,
                    'placeholder': 'Provide specific details, color, brand, condition, or identifiers...',
                    'required': True,
                }
            ),
            'location': forms.TextInput(
                attrs={
                    'class': 'form-input',
                    'placeholder': 'e.g., Main Library 2nd Floor, Science Center Rm 101',
                    'required': True,
                }
            ),
            'date_lost_or_found': forms.DateInput(
                attrs={
                    'class': 'form-input',
                    'type': 'date',
                    'required': True,
                }
            ),
            'contact_info': forms.TextInput(
                attrs={
                    'class': 'form-input',
                    'placeholder': 'e.g., student@campus.edu or 555-0192 (optional)',
                }
            ),
            'image': forms.FileInput(
                attrs={
                    'class': 'form-input-file',
                    'accept': 'image/jpeg,image/png,image/webp,image/gif',
                }
            ),
        }
        labels = {
            'title': 'Item Title',
            'item_type': 'Report Type',
            'category': 'Category',
            'description': 'Description',
            'location': 'Campus Location',
            'date_lost_or_found': 'Date Lost or Found',
            'contact_info': 'Contact Info (Optional)',
            'image': 'Photograph (Optional)',
        }
        help_texts = {
            'title': 'Provide a concise, recognizable title.',
            'item_type': 'Indicate whether you lost this item or found it.',
            'location': 'Specific building, floor, room, or landmark on campus.',
            'date_lost_or_found': 'The date the item was misplaced or discovered (cannot be in the future).',
            'contact_info': 'Email or phone for other students/staff to reach you.',
            'image': 'Upload an optional photograph (JPEG, PNG, WebP, or GIF, max 5MB).',
        }
        error_messages = {
            'title': {
                'required': 'Please enter an item title.',
                'max_length': 'Item title cannot exceed 100 characters.',
            },
            'description': {
                'required': 'Please provide a detailed description.',
            },
            'location': {
                'required': 'Please specify the campus location.',
                'max_length': 'Location cannot exceed 150 characters.',
            },
            'date_lost_or_found': {
                'required': 'Please select the date the item was lost or found.',
                'invalid': 'Please enter a valid date in YYYY-MM-DD format.',
            },
        }

    def clean_date_lost_or_found(self):
        date = self.cleaned_data.get('date_lost_or_found')
        if date and date > timezone.localdate():
            raise forms.ValidationError("Date cannot be in the future.")
        return date

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if not image:
            return image

        # 1. Enforce max file size: 5 MB
        max_size = 5 * 1024 * 1024
        if image.size > max_size:
            raise forms.ValidationError("Image file size cannot exceed 5MB.")

        # 2. Validate actual image integrity and format using Pillow
        try:
            image.seek(0)
            pil_img = Image.open(image)
            pil_img.verify()

            allowed_formats = {'JPEG', 'PNG', 'WEBP', 'GIF'}
            if pil_img.format and pil_img.format.upper() not in allowed_formats:
                raise forms.ValidationError(
                    f"Unsupported image format ({pil_img.format}). Allowed formats: JPEG, PNG, WebP, GIF."
                )
            image.seek(0)
        except forms.ValidationError:
            raise
        except Exception:
            raise forms.ValidationError("Upload a valid image. The file you uploaded was either not an image or a corrupted image.")

        return image
