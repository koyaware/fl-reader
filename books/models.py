import uuid
from django.db import models

class Book(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    cover = models.ImageField(upload_to='covers/', blank=True, null=True)
    file = models.FileField(upload_to='books/')
    flibusta_id = models.CharField(max_length=100, blank=True, null=True)
    reading_progress = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.author}"
