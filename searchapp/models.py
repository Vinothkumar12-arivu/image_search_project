# E:\Project\searchapp\models.py
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

class ImageItem(models.Model):
    filename = models.CharField(max_length=255)
    file_relative_path = models.CharField(max_length=1024, unique=True)
    extracted_text = models.TextField(blank=True)
    indexed_at = models.DateTimeField(auto_now=True)
    page_number = models.IntegerField(default=0)  # <- NEW line to track PDF page


class UploadedFile(models.Model):
    file = models.FileField(upload_to='uploads/')  # stored in MEDIA_ROOT/uploads/
    uploaded_at = models.DateTimeField(auto_now_add=True)



    def get_url(self):
        return settings.MEDIA_URL + self.file_relative_path.replace('\\', '/')

    def __str__(self):
        if self.page_number:
            return f"{self.filename} - Page {self.page_number}"
        return self.filename

    
