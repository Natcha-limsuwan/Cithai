from django.db import models
from .enums import GenerationStatus, Mood, Genre, Occasion, VoiceType
from .user import User


class Song(models.Model):
    """
    Central entity. Belongs to exactly one User (C-1).
    A User may own a maximum of 20 Songs (C-2).
    isShared defaults to False (C-3).
    Audio file is stored externally; only metadata is kept here (A-7).
    """
    song_id       = models.AutoField(primary_key=True)
    user          = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="songs",
    )
    title         = models.CharField(max_length=255)
    custom_lyrics = models.TextField(blank=True, null=True)
    duration      = models.IntegerField(null=True, blank=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    is_shared     = models.BooleanField(default=False)  # C-3

    audio_url  = models.URLField(null=True, blank=True)  # A-7: external storage

    status     = models.CharField(max_length=20, choices=GenerationStatus.choices, default=GenerationStatus.PENDING)
    mood       = models.CharField(max_length=20, choices=Mood.choices)
    genre      = models.CharField(max_length=20, choices=Genre.choices)
    occasion   = models.CharField(max_length=20, choices=Occasion.choices)
    voice_type = models.CharField(max_length=20, choices=VoiceType.choices)

    class Meta:
        app_label = "core"
        verbose_name = "Song"
        ordering = ["-creation_date"]

    def __str__(self):
        return f"{self.title} ({self.status})"

    def save(self, *args, **kwargs):
        # C-2: enforce 20-song limit per user on create
        if not self.pk:
            if Song.objects.filter(user=self.user).count() >= 20:
                raise ValueError("A user may not own more than 20 songs (C-2).")
        super().save(*args, **kwargs)