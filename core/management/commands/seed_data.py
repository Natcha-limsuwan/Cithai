"""
Management command: python manage.py seed_data
Creates demo Users, Songs, MusicGenerationRequests, and ShareLinks.
Safe to run multiple times (idempotent by email).
"""
from django.core.management.base import BaseCommand
from core.models import User, Song, MusicGenerationRequest, ShareLink, GenerationStatus


class Command(BaseCommand):
    help = "Seed the database with sample domain data"

    def handle(self, *args, **options):
        # Users
        u1, _ = User.objects.get_or_create(
            email="alice@example.com",
            defaults={"google_id": "google_alice_001", "name": "Alice"},
        )
        u2, _ = User.objects.get_or_create(
            email="bob@example.com",
            defaults={"google_id": "google_bob_002", "name": "Bob"},
        )
        self.stdout.write(f"Users: {u1}, {u2}")

        # Songs
        s1, _ = Song.objects.get_or_create(
            user=u1, title="Happy Birthday Tune",
            defaults={
                "mood": "Happy", "genre": "Pop", "occasion": "Birthday",
                "voice_type": "Female", "status": "Complete", "duration": 180,
            },
        )
        s2, _ = Song.objects.get_or_create(
            user=u1, title="Wedding Waltz",
            defaults={
                "mood": "Romantic", "genre": "Classical", "occasion": "Wedding",
                "voice_type": "Duet", "status": "Processing",
            },
        )
        s3, _ = Song.objects.get_or_create(
            user=u1, title="Graduation Rock",
            defaults={
                "mood": "Energetic", "genre": "Rock", "occasion": "Graduation",
                "voice_type": "Male", "status": "Failed",
            },
        )
        Song.objects.get_or_create(
            user=u2, title="Bob's Jazz Night",
            defaults={
                "mood": "Calm", "genre": "Jazz", "occasion": "Anniversary",
                "voice_type": "Instrumental", "status": "Complete", "duration": 240,
            },
        )
        self.stdout.write(f"Songs created: {s1}, {s2}, {s3}")

        # MusicGenerationRequest — preserved for failed song (C-7)
        req, _ = MusicGenerationRequest.objects.get_or_create(
            user=u1, song=s3,
            defaults={
                "title": "Graduation Rock", "mood": "Energetic", "genre": "Rock",
                "occasion": "Graduation", "voice_type": "Male", "is_retry": False,
            },
        )
        self.stdout.write(f"Request: {req}")

        # ShareLink for completed song (C-4)
        if not hasattr(s1, "share_link") or not ShareLink.objects.filter(song=s1).exists():
            link = ShareLink.objects.create(song=s1, is_active=True)
            self.stdout.write(f"ShareLink: {link}")
        else:
            self.stdout.write("ShareLink already exists — skipped")

        self.stdout.write(self.style.SUCCESS("Seed data applied successfully."))
