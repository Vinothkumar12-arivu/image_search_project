from django.shortcuts import render, redirect
from .forms import SearchForm
from .models import ImageItem
from django.db.models import Q  # <-- NEW
from .forms import UploadFileForm
from .models import UploadedFile
import os
from django.conf import settings
from PyPDF2 import PdfReader
from django.core.files.storage import FileSystemStorage


def search_view(request):
    q = request.GET.get('q', '').strip()
    results = []
    matches = []   # <-- NEW: make sure matches always exists

    if q:
        # simple case-insensitive substring search on extracted_text
             
             ##results = ImageItem.objects.filter(
             matches = ImageItem.objects.filter(
                Q(extracted_text__icontains=q) | Q(filename__icontains=q)   # <-- UPDATED LINE
    ).order_by('-indexed_at')
             
    form = SearchForm(initial={'q': q})



  # ---------- NEW: Remove duplicates by filename ----------
    seen_files = set()
    for item in matches:
            if item.filename not in seen_files:
                results.append(item)
                seen_files.add(item.filename)
        # ---------------------------------------------------------


    return render(
          request, 'searchapp/search.html', 
          {'form': form, 'results': results, 'query': q})


def download_file(request):
    files = UploadedFile.objects.all()
    query = request.GET.get('q')
    if query:
        files = files.filter(file__icontains=query)
    return render(request, 'searchapp/download.html', {'files': files})





def upload_view(request):
    if request.method == 'POST' and request.FILES.get('file'):
        upload = request.FILES['file']
        fs = FileSystemStorage(location=settings.MEDIA_ROOT / 'uploads')
        filename = fs.save(upload.name, upload)
        UploadedFile.objects.create(file='uploads/' + filename)
        return render(request, 'upload_success.html', {'filename': filename})
    return render(request, 'searchapp/upload.html')
