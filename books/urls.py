from django.urls import path
from . import views

app_name = 'books'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('book/<uuid:pk>/', views.BookDetailView.as_view(), name='book_detail'),
    path('book/<uuid:pk>/progress/', views.UpdateProgressView.as_view(), name='update_progress'),
    path('search/', views.SearchView.as_view(), name='search'),
    path('download/', views.DownloadView.as_view(), name='download'),
    path('book/<uuid:pk>/delete/', views.DeleteBookView.as_view(), name='delete_book'),
]
