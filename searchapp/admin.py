# E:\Project\searchapp\admin.py
from django.contrib import admin
from .models import ImageItem

@admin.register(ImageItem)
class ImageItemAdmin(admin.ModelAdmin):
    list_display = ('filename', 'file_relative_path', 'indexed_at')
    search_fields = ('filename', 'extracted_text')
