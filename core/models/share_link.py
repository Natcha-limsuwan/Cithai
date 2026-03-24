import uuid
from django.db import models
from .enums import GenerationStatus
from .song import Song


class ShareLink(models.Model):
    """
    A unique URL token that allows authenticated users to access a private Song.
    Only created for Songs with status = Complete (C-4, A-5).
    A Song may have 0 or 1 ShareLink (A-4).
    """
    link_id    = models.AutoField(primary_key=True)
    song       = models.OneToOneField(Song, on_delete=models.CASCADE, related_name="share_link")
    token      = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active  = models.BooleanField(default=True)

    class Meta:
        app_label = "core"
        verbose_name = "Share Link"

    def __str__(self):
        return f"ShareLink for '{self.song.title}' ({'active' if self.is_active else 'inactive'})"

    def save(self, *args, **kwargs):
        # C-4 / A-5: only Complete songs can be shared
        if self.song.status != GenerationStatus.COMPLETE:
            raise ValueError("A ShareLink can only be created for a song with status 'Complete'.")
        super().save(*args, **kwargs)