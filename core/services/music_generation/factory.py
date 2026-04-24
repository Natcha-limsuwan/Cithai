from django.conf import settings

from .base import MusicGenerationError
from .mock_strategy import MockMusicGenerationStrategy
from .suno_strategy import SunoMusicGenerationStrategy


def get_music_generation_strategy(provider: str | None = None):
    resolved = (provider or settings.GENERATOR_STRATEGY).lower()
    if resolved == "mock":
        return MockMusicGenerationStrategy()
    if resolved == "suno":
        return SunoMusicGenerationStrategy()
    raise MusicGenerationError(f"Unsupported provider '{resolved}'.")
