from .base import GenerationResult, MusicGenerationStrategy
from ...models import GenerationStatus

_SAMPLE_URLS = [
    "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
    "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3",
    "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3",
    "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-4.mp3",
    "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-5.mp3",
    "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-6.mp3",
    "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-7.mp3",
    "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-8.mp3",
]


class MockMusicGenerationStrategy(MusicGenerationStrategy):
    provider_name = "mock"

    def generate(self, generation_request):
        audio_url = _SAMPLE_URLS[generation_request.request_id % len(_SAMPLE_URLS)]
        return GenerationResult(
            status=GenerationStatus.COMPLETE,
            provider_name=self.provider_name,
            provider_task_id=f"mock-{generation_request.request_id}",
            duration=180,
            title=generation_request.title,
            audio_url=audio_url,
            raw_response={"provider": "mock", "mode": "instant"},
        )

    def refresh(self, generation_request):
        return self.generate(generation_request)
