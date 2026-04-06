from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone
from django.views import View
from .models import Book
from .services import flibusta_service, fb2_parser, reading_service


def is_htmx(request):
    return request.headers.get('HX-Request') == 'true'


class IndexView(View):
    def get(self, request):
        books = Book.objects.all().order_by('-created_at')
        context = {
            'books': books, 
            'is_htmx': is_htmx(request),
            'active_tab': 'library'
        }
        if is_htmx(request):
            return render(request, 'books/partials/library_content.html', context)
        return render(request, 'books/index.html', context)


class FavoritesView(View):
    def get(self, request):
        books = Book.objects.filter(is_favorite=True).order_by('-created_at')
        context = {
            'books': books, 
            'is_htmx': is_htmx(request),
            'active_tab': 'favorites'
        }
        if is_htmx(request):
            return render(request, 'books/partials/favorites_content.html', context)
        return render(request, 'books/favorites.html', context)




class BookDetailView(View):
    def get(self, request, pk):
        book = get_object_or_404(Book, pk=pk)
        
        # Обновляем время последнего чтения
        book.last_read_at = timezone.now()
        book.save(update_fields=['last_read_at'])
        
        content = reading_service.get_book_content(book)
        context = {
            'book': book, 
            'content': content, 
            'is_htmx': is_htmx(request),
            'hide_tabbar': True,
            'active_tab': 'reading'
        }
        if is_htmx(request):
            return render(request, 'books/partials/reader_content.html', context)
        return render(request, 'books/book_detail.html', context)


class LastReadRedirectView(View):
    def get(self, request):
        last_book = Book.objects.exclude(last_read_at__isnull=True).order_by('-last_read_at').first()
        if last_book:
            url = f"/book/{last_book.id}/"
            if is_htmx(request):
                response = HttpResponse(status=204)
                response['HX-Location'] = url
                return response
            return redirect('books:book_detail', pk=last_book.id)
        return redirect('books:index')


class UpdateProgressView(View):
    def post(self, request, pk):
        book = get_object_or_404(Book, pk=pk)
        try:
            progress = max(0, min(100, int(request.POST.get('progress', 0))))
        except (ValueError, TypeError):
            progress = 0
        book.reading_progress = progress
        book.save(update_fields=['reading_progress'])
        return HttpResponse(status=204)


class LibrarySearchView(View):
    def get(self, request):
        query = request.GET.get('q', '').strip()
        books = Book.objects.all().order_by('-created_at')
        if query:
            from django.db.models import Q
            books = books.filter(Q(title__icontains=query) | Q(author__icontains=query))
        context = {'books': books, 'query': query}
        return render(request, 'books/partials/book_grid.html', context)


class SearchView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return HttpResponse(
                '<div class="p-8 text-center glass rounded-3xl"><p class="text-white/40">Поиск по Флибусте доступен только авторизованным администраторам.</p></div>',
                status=401
            )
        
        query = request.GET.get('q', '').strip()
        results = []
        error = None
        if query:
            results = flibusta_service.search_books(query)
            if results is None:
                error = 'Не удалось подключиться к Флибусте. Убедитесь, что Tor запущен.'
                results = []
        context = {'results': results, 'query': query, 'error': error}
        return render(request, 'books/partials/search_results.html', context)


class DownloadView(View):
    def post(self, request):
        if not request.user.is_authenticated:
            return HttpResponse('<p class="text-red-400 text-sm p-4">Авторизация обязательна</p>', status=401)
            
        flibusta_id = request.POST.get('flibusta_id', '').strip()
        if not flibusta_id:
            return HttpResponse('<p class="text-red-400 text-sm p-4">Не указан ID книги</p>', status=400)

        book_file = flibusta_service.download_book(flibusta_id)
        if not book_file:
            return HttpResponse(
                '<p class="text-red-400 text-sm p-4">Не удалось скачать книгу. Проверьте соединение с Tor.</p>',
                status=500
            )

        metadata = fb2_parser.parse_metadata(book_file)
        book = Book.objects.create(
            title=metadata.get('title', 'Unknown Title'),
            author=metadata.get('author', 'Unknown Author'),
            flibusta_id=flibusta_id,
        )
        book.file.save(f'{book.id}.fb2', book_file)

        if metadata.get('cover'):
            cover_file = metadata['cover']
            ext = 'jpg'
            if hasattr(cover_file, 'name') and cover_file.name:
                ext = cover_file.name.rsplit('.', 1)[-1]
            book.cover.save(f'{book.id}_cover.{ext}', cover_file)

        book.refresh_from_db()
        
        # Рендерим новую карточку книги
        book_html = render(request, 'books/partials/book_card.html', {'book': book}).content.decode('utf-8')
        
        # OOB свап для кнопки "Скачать", чтобы превратить её в зелёную галочку "Скачано"
        oob_btn = f'''
        <button id="dl-btn-{flibusta_id}" hx-swap-oob="true" disabled
                class="shrink-0 px-4 py-2 bg-green-600/50 rounded-xl text-xs font-semibold text-green-100 flex items-center gap-2 whitespace-nowrap cursor-default">
            <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"/>
            </svg>
            Скачано
        </button>
        '''
        
        return HttpResponse(book_html + oob_btn, status=200)


class DeleteBookView(View):
    def delete(self, request, pk):
        book = get_object_or_404(Book, pk=pk)
        if book.file:
            book.file.delete(save=False)
        if book.cover:
            book.cover.delete(save=False)
        book.delete()
        return HttpResponse(status=200)

class ToggleFavoriteView(View):
    def post(self, request, pk):
        book = get_object_or_404(Book, pk=pk)
        book.is_favorite = not book.is_favorite
        book.save(update_fields=['is_favorite'])
        return render(request, 'books/partials/favorite_button.html', {'book': book})

