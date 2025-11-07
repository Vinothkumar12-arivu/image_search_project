from django.urls import path
from . import views

urlpatterns = [
    path('search/', views.search_view, name='search'),
    path('', views.search_view, name='search'),

    path('upload/', views.upload_view, name='upload'),  # 🟢 New Line
    #path('download/', views.download_file, name='download_file'),  # old search/download page
]
