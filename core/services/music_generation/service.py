from django.db import transaction

from ...models import Song
from .base import MusicGenerationError
from .factory import get_music_generation_strategy


class MusicGenerationService:
    def __init__(self, strategy=None):
        self.strategy = strategy or get_music_generation_strategy()

    def _build_or_get_song(self, generation_request, result):
        song = generation_request.song or Song(user=generation_request.user)
        song.title = result.title or generation_request.title
        song.custom_lyrics = generation_request.custom_lyrics
        song.mood = generation_request.mood
        song.genre = generation_request.genre
        song.occasion = generation_request.occasion
        song.voice_type = generation_request.voice_type
        song.duration = result.duration
        song.audio_url = result.audio_url
        song.status = result.status
        song.save()
        return song

    @transaction.atomic
    def submit_request(self, generation_request):
        result = self.strategy.generate(generation_request)
        song = self._build_or_get_song(generation_request, result)

        generation_request.song = song
        generation_request.generation_provider = result.provider_name
        generation_request.provider_task_id = result.provider_task_id
        generation_request.provider_status_message = result.error_message
        generation_request.save(
            update_fields=[
                "song",
                "generation_provider",
                "provider_task_id",
                "provider_status_message",
            ]
        )
        return generation_request

    @transaction.atomic
    def refresh_request(self, generation_request):
        if not generation_request.song and not generation_request.provider_task_id:
            raise MusicGenerationError(
                "Cannot refresh a request before a song or provider task id has been created."
            )

        result = self.strategy.refresh(generation_request)
        song = self._build_or_get_song(generation_request, result)

        generation_request.song = song
        generation_request.generation_provider = result.provider_name
        generation_request.provider_task_id = result.provider_task_id
        generation_request.provider_status_message = result.error_message
        generation_request.save(
            update_fields=[
                "song",
                "generation_provider",
                "provider_task_id",
                "provider_status_message",
            ]
        )
        return generation_request
