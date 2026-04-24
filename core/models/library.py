from django.db import models
from .user import User
from .song import Song


class Library(models.Model):
    library_id  = models.AutoField(primary_key=True)
    name        = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    user        = models.ForeignKey(User, on_delete=models.CASCADE, related_name="libraries")
    songs       = models.ManyToManyField(Song, related_name="libraries", blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "libraries"

    def __str__(self):
        return f"{self.name} ({self.user.email})"
