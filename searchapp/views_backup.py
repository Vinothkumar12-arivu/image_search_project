from django.shortcuts import render
from .forms import SearchForm
from .models import ImageItem
from django.db.models import Q  # <-- NEW

def search_view(request):
    q = request.GET.get('q', '').strip()
    results = []
    if q:
        # simple case-insensitive substring search on extracted_text
         results = ImageItem.objects.filter(
        Q(extracted_text__icontains=q) | Q(filename__icontains=q)   # <-- UPDATED LINE
    ).order_by('-indexed_at')
    form = SearchForm(initial={'q': q})
    return render(request, 'searchapp/search.html', {'form': form, 'results': results, 'query': q})
