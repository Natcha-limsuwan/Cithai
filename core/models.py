from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
import uuid


# ── Enumerations ────────────────────────────────────────────────────────────

class Mood(models.TextChoices):
    HAPPY     = "Happy",      "Happy"
    SAD       = "Sad",        "Sad"
    ROMANTIC  = "Romantic",   "Romantic"
    ENERGETIC = "Energetic",  "Energetic"
    CALM      = "Calm",       "Calm"


class Genre(models.TextChoices):
    POP       = "Pop",       "Pop"
    ROCK      = "Rock",      "Rock"
    JAZZ      = "Jazz",      "Jazz"
    CLASSICAL = "Classical", "Classical"
    HIPHOP    = "HipHop",    "HipHop"


class Occasion(models.TextChoices):
    BIRTHDAY    = "Birthday",    "Birthday"
    WEDDING     = "Wedding",     "Wedding"
    GRADUATION  = "Graduation",  "Graduation"
    ANNIVERSARY = "Anniversary", "Anniversary"
    CUSTOM      = "Custom",      "Custom"


class VoiceType(models.TextChoices):
    MALE         = "Male",         "Male"
    FEMALE       = "Female",       "Female"
    CHILD        = "Child",        "Child"
    CHOIR        = "Choir",        "Choir"
    INSTRUMENTAL = "Instrumental", "Instrumental"
    DUET         = "Duet",         "Duet"


class GenerationStatus(models.TextChoices):
    PENDING    = "Pending",    "Pending"
    PROCESSING = "Processing", "Processing"
    COMPLETE   = "Complete",   "Complete"
    FAILED     = "Failed",     "Failed"


# ── User ────────────────────────────────────────────────────────────────────

class UserManager(BaseUserManager):
    def create_user(self, username, name="", google_id="", email="", **extra_fields):
        user = self.model(username=username, email=email, google_id=google_id, name=name, **extra_fields)
        user.set_password(extra_fields.pop("password", None))
        user.save(using=self._db)
        return user

    def create_superuser(self, username, name="Admin", google_id=None, email="", **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(username, name=name, google_id=google_id, email=email, **extra_fields)


class User(AbstractBaseUser):
    """
    Authenticated person using Cithai.
    Identity is managed entirely via Google OAuth (A-1).
    """
    user_id    = models.AutoField(primary_key=True)
    username   = models.CharField(max_length=150, unique=True, blank=True, default="")
    google_id  = models.CharField(max_length=255, blank=True, null=True, default=None)
    email      = models.EmailField(unique=True, blank=True, default="")
    name       = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    is_active    = models.BooleanField(default=True)
    is_staff     = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD  = "username"
    REQUIRED_FIELDS = ["name"]

    objects = UserManager()

    class Meta:
        verbose_name = "User"

    def __str__(self):
        return f"{self.name} ({self.username})"

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser


# ── Song ────────────────────────────────────────────────────────────────────

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
    is_shared     = models.BooleanField(default=False)   # C-3

    status     = models.CharField(
        max_length=20,
        choices=GenerationStatus.choices,
        default=GenerationStatus.PENDING,
    )
    mood       = models.CharField(max_length=20, choices=Mood.choices)
    genre      = models.CharField(max_length=20, choices=Genre.choices)
    occasion   = models.CharField(max_length=20, choices=Occasion.choices)
    voice_type = models.CharField(max_length=20, choices=VoiceType.choices)

    class Meta:
        verbose_name = "Song"
        ordering = ["-creation_date"]

    def __str__(self):
        return f"{self.title} ({self.status})"

    def save(self, *args, **kwargs):
        # C-2: enforce 20-song limit per user on create
        if not self.pk:
            count = Song.objects.filter(user=self.user).count()
            if count >= 20:
                raise ValueError("A user may not own more than 20 songs (C-2).")
        super().save(*args, **kwargs)


# ── MusicGenerationRequest ───────────────────────────────────────────────────

class MusicGenerationRequest(models.Model):
    """
    Input data submitted by a User to generate a Song.
    Preserved on failure so the user can retry without re-entering data (C-7, A-2).
    One request produces at most one Song (A-2).
    """
    request_id    = models.AutoField(primary_key=True)
    user          = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="generation_requests",
    )
    song          = models.OneToOneField(
        Song,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="generation_request",
    )

    title         = models.CharField(max_length=255)
    custom_lyrics = models.TextField(blank=True, null=True)
    occasion      = models.CharField(max_length=20, choices=Occasion.choices)
    genre         = models.CharField(max_length=20, choices=Genre.choices)
    voice_type    = models.CharField(max_length=20, choices=VoiceType.choices)
    mood          = models.CharField(max_length=20, choices=Mood.choices)

    submitted_at  = models.DateTimeField(auto_now_add=True)
    is_retry      = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Music Generation Request"
        ordering = ["-submitted_at"]

    def __str__(self):
        retry_tag = " [retry]" if self.is_retry else ""
        return f"Request '{self.title}' by {self.user}{retry_tag}"


# ── ShareLink ────────────────────────────────────────────────────────────────

class ShareLink(models.Model):
    """
    A unique URL token that allows authenticated users to access a private Song.
    Only created for Songs with status = Complete (C-4, A-5).
    A Song may have 0 or 1 ShareLink (A-4).
    """
    link_id    = models.AutoField(primary_key=True)
    song       = models.OneToOneField(
        Song,
        on_delete=models.CASCADE,
        related_name="share_link",
    )
    token      = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active  = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Share Link"

    def __str__(self):
        return f"ShareLink for '{self.song.title}' ({'active' if self.is_active else 'inactive'})"

    def save(self, *args, **kwargs):
        # C-4 / A-5: only Complete songs can be shared
        if self.song.status != GenerationStatus.COMPLETE:
            raise ValueError(
                "A ShareLink can only be created for a song with status 'Complete' (C-4)."
            )
        super().save(*args, **kwargs)