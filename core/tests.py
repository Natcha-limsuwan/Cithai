from unittest.mock import patch

from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from core.models import GenerationStatus, MusicGenerationRequest, Song, User
from core.services.music_generation import get_music_generation_strategy
from core.services.music_generation.base import GenerationResult


class MusicGenerationStrategyTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(email="user@example.com", name="User")

    @override_settings(GENERATOR_STRATEGY="mock")
    def test_factory_returns_mock_strategy(self):
        strategy = get_music_generation_strategy()
        self.assertEqual(strategy.provider_name, "mock")

    @override_settings(GENERATOR_STRATEGY="mock")
    def test_create_request_generates_song_with_mock_strategy(self):
        client = APIClient()
        response = client.post(
            "/api/requests/",
            {
                "user": self.user.pk,
                "title": "Peaceful Piano",
                "custom_lyrics": "",
                "occasion": "Custom",
                "genre": "Classical",
                "voice_type": "Instrumental",
                "mood": "Calm",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        generation_request = MusicGenerationRequest.objects.get(pk=response.data["request_id"])
        self.assertEqual(generation_request.generation_provider, "mock")
        self.assertTrue(generation_request.provider_task_id.startswith("mock-"))
        self.assertIsNotNone(generation_request.song)
        self.assertEqual(generation_request.song.status, GenerationStatus.COMPLETE)
        self.assertEqual(generation_request.song.duration, 180)

    @override_settings(GENERATOR_STRATEGY="suno")
    @patch("core.services.music_generation.suno_strategy.SunoMusicGenerationStrategy.refresh")
    def test_refresh_generation_updates_song_status(self, mock_refresh):
        generation_request = MusicGenerationRequest.objects.create(
            user=self.user,
            title="Festival Night",
            custom_lyrics="",
            occasion="Custom",
            genre="Pop",
            voice_type="Female",
            mood="Energetic",
            generation_provider="suno",
            provider_task_id="task-123",
        )
        song = Song.objects.create(
            user=self.user,
            title="Festival Night",
            custom_lyrics="",
            occasion="Custom",
            genre="Pop",
            voice_type="Female",
            mood="Energetic",
            status=GenerationStatus.PROCESSING,
        )
        generation_request.song = song
        generation_request.save(update_fields=["song"])

        mock_refresh.return_value = GenerationResult(
            status=GenerationStatus.COMPLETE,
            provider_name="suno",
            provider_task_id="task-123",
            duration=198,
            title="Festival Night Final",
            audio_url="https://cdn.example.com/festival-night.mp3",
        )

        client = APIClient()
        response = client.post(f"/api/requests/{generation_request.pk}/refresh_generation/")

        self.assertEqual(response.status_code, 200)
        generation_request.refresh_from_db()
        generation_request.song.refresh_from_db()
        self.assertEqual(generation_request.song.status, GenerationStatus.COMPLETE)
        self.assertEqual(generation_request.song.duration, 198)
        self.assertEqual(generation_request.song.title, "Festival Night Final")
        self.assertEqual(generation_request.song.audio_url, "https://cdn.example.com/festival-night.mp3")

    @override_settings(GENERATOR_STRATEGY="suno")
    @patch("core.services.music_generation.suno_strategy.SunoMusicGenerationStrategy.refresh")
    def test_refresh_generation_creates_song_when_task_exists_but_song_is_missing(self, mock_refresh):
        generation_request = MusicGenerationRequest.objects.create(
            user=self.user,
            title="Festival Night",
            custom_lyrics="Shine through the city lights",
            occasion="Custom",
            genre="Pop",
            voice_type="Female",
            mood="Energetic",
            generation_provider="suno",
            provider_task_id="task-456",
        )

        mock_refresh.return_value = GenerationResult(
            status=GenerationStatus.PROCESSING,
            provider_name="suno",
            provider_task_id="task-456",
            duration=None,
            title="Festival Night",
            audio_url="https://cdn.example.com/festival-night-preview.mp3",
        )

        client = APIClient()
        response = client.post(f"/api/requests/{generation_request.pk}/refresh_generation/")

        self.assertEqual(response.status_code, 200)
        generation_request.refresh_from_db()
        self.assertIsNotNone(generation_request.song)
        generation_request.song.refresh_from_db()
        self.assertEqual(generation_request.song.status, GenerationStatus.PROCESSING)
        self.assertEqual(generation_request.song.title, "Festival Night")
        self.assertEqual(generation_request.song.audio_url, "https://cdn.example.com/festival-night-preview.mp3")
