from django.urls import path
from . import views

app_name = 'books'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('favorites/', views.FavoritesView.as_view(), name='favorites'),
    path('last-read/', views.LastReadRedirectView.as_view(), name='last_read'),
    path('book/<uuid:pk>/', views.BookDetailView.as_view(), name='book_detail'),
    path('book/<uuid:pk>/progress/', views.UpdateProgressView.as_view(), name='update_progress'),
    path('book/<uuid:pk>/favorite/', views.ToggleFavoriteView.as_view(), name='toggle_favorite'),
    path('book/<uuid:pk>/delete/', views.DeleteBookView.as_view(), name='delete_book'),
    path('search/', views.SearchView.as_view(), name='search'),
    path('library/search/', views.LibrarySearchView.as_view(), name='library_search'),
    path('download/', views.DownloadView.as_view(), name='download'),
]
