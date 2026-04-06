from django.views.generic import ListView, DetailView, View
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from .models import Book
from .services import flibusta_service, fb2_parser, reading_service

class IndexView(ListView):
    model = Book
    template_name = 'books/index.html'
    context_object_name = 'books'
    ordering = ['-created_at']

class BookDetailView(DetailView):
    model = Book
    template_name = 'books/book_detail.html'
    context_object_name = 'book'

class UpdateProgressView(View):
    def post(self, request, pk):
        book = get_object_or_404(Book, pk=pk)
        progress = request.POST.get('progress', 0)
        book.reading_progress = int(progress)
        book.save()
        return JsonResponse({'status': 'success'})

class SearchView(View):
    def get(self, request):
        query = request.GET.get('q', '')
        results = []
        if query:
            results = flibusta_service.search_books(query)
        return JsonResponse({'results': results})

class DownloadView(View):
    def post(self, request):
        flibusta_id = request.POST.get('flibusta_id')
        if not flibusta_id:
            return JsonResponse({'error': 'No flibusta_id provided'}, status=400)
        
        book_file = flibusta_service.download_book(flibusta_id)
        if not book_file:
            return JsonResponse({'error': 'Failed to download'}, status=500)
            
        metadata = fb2_parser.parse_metadata(book_file)
        
        book = Book.objects.create(
            title=metadata.get('title', 'Unknown Title'),
            author=metadata.get('author', 'Unknown Author'),
            flibusta_id=flibusta_id
        )
        
        book.file.save(f'{book.id}.fb2', book_file)
        
        if metadata.get('cover'):
            book.cover.save(f'{book.id}_cover.jpg', metadata['cover'])
            
        return JsonResponse({'status': 'success', 'book_id': str(book.id)})

class DeleteBookView(View):
    def delete(self, request, pk):
        book = get_object_or_404(Book, pk=pk)
        book.delete()
        return JsonResponse({'status': 'success'})
