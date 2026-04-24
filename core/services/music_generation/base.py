from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class GenerationResult:
    status: str
    provider_name: str
    provider_task_id: str = ""
    duration: int | None = None
    title: str | None = None
    audio_url: str | None = None
    error_message: str = ""
    raw_response: dict = field(default_factory=dict)


class MusicGenerationError(Exception):
    """Raised when a generation provider cannot complete the request."""


class MusicGenerationStrategy(ABC):
    provider_name = "base"

    @abstractmethod
    def generate(self, generation_request):
        """Generate or submit a song request and return a normalized result."""

    def submit(self, generation_request):
        """Backward-compatible alias used by the service layer."""
        return self.generate(generation_request)

    @abstractmethod
    def refresh(self, generation_request):
        """Refresh the provider status for an existing request."""
