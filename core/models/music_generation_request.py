from django.db import models
from .enums import Mood, Genre, Occasion, VoiceType
from .user import User
from .song import Song


class MusicGenerationRequest(models.Model):
    """
    Input data submitted by a User to generate a Song.
    Preserved on failure so the user can retry without re-entering data (C-7, A-2).
    One request produces at most one Song (A-2).
    """
    request_id    = models.AutoField(primary_key=True)
    user          = models.ForeignKey(User, on_delete=models.CASCADE, related_name="generation_requests")
    song          = models.OneToOneField(Song, on_delete=models.SET_NULL, null=True, blank=True, related_name="generation_request")

    title         = models.CharField(max_length=255)
    custom_lyrics = models.TextField(blank=True, null=True)
    occasion      = models.CharField(max_length=20, choices=Occasion.choices)
    genre         = models.CharField(max_length=20, choices=Genre.choices)
    voice_type    = models.CharField(max_length=20, choices=VoiceType.choices)
    mood          = models.CharField(max_length=20, choices=Mood.choices)

    submitted_at  = models.DateTimeField(auto_now_add=True)
    is_retry      = models.BooleanField(default=False)

    class Meta:
        app_label = "core"
        verbose_name = "Music Generation Request"
        ordering = ["-submitted_at"]

    def __str__(self):
        retry_tag = " [retry]" if self.is_retry else ""
        return f"Request '{self.title}' by {self.user}{retry_tag}"