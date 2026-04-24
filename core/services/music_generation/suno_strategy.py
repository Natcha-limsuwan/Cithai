import json
from urllib import error, parse, request

from django.conf import settings

from .base import GenerationResult, MusicGenerationError, MusicGenerationStrategy
from ...models import GenerationStatus


class SunoMusicGenerationStrategy(MusicGenerationStrategy):
    provider_name = "suno"

    def _headers(self):
        if not settings.SUNO_API_KEY:
            raise MusicGenerationError(
                "SUNO_API_KEY is not configured. Switch to MUSIC_GENERATION_PROVIDER=mock or set the API key."
            )
        return {
            "Authorization": f"Bearer {settings.SUNO_API_KEY}",
            "Content-Type": "application/json",
            "Accept": "*/*",
            "User-Agent": "curl/8.7.1",
        }

    def _request_json(self, method, path, payload=None, query=None):
        url = f"{settings.SUNO_API_BASE_URL.rstrip('/')}/{path.lstrip('/')}"
        if query:
            url = f"{url}?{parse.urlencode(query)}"

        body = None
        if payload is not None:
            body = json.dumps(payload).encode("utf-8")

        req = request.Request(url, data=body, headers=self._headers(), method=method)
        try:
            with request.urlopen(req, timeout=30) as response:
                return json.loads(response.read().decode("utf-8"))
        except error.HTTPError as exc:
            details = exc.read().decode("utf-8", errors="replace")
            raise MusicGenerationError(f"Suno API error {exc.code}: {details}") from exc
        except error.URLError as exc:
            raise MusicGenerationError(f"Could not reach Suno API: {exc.reason}") from exc

    def _build_payload(self, generation_request):
        instrumental = generation_request.voice_type == "Instrumental"
        prompt = generation_request.custom_lyrics or (
            f"{generation_request.mood} {generation_request.genre} music for "
            f"{generation_request.occasion}"
        )
        return {
            "customMode": True,
            "instrumental": instrumental,
            "model": settings.SUNO_MODEL,
            "callBackUrl": settings.SUNO_CALLBACK_URL,
            "prompt": prompt,
            "style": generation_request.genre,
            "title": generation_request.title,
        }

    def _map_status(self, suno_status):
        if suno_status == "SUCCESS":
            return GenerationStatus.COMPLETE
        if suno_status in {"PENDING", "TEXT_SUCCESS", "FIRST_SUCCESS"}:
            return GenerationStatus.PROCESSING
        return GenerationStatus.FAILED

    def generate(self, generation_request):
        payload = self._build_payload(generation_request)
        response = self._request_json("POST", "generate", payload=payload)
        if response.get("code") != 200:
            raise MusicGenerationError(response.get("msg", "Failed to create Suno task."))

        task_id = str(response.get("data", {}).get("taskId", ""))
        if not task_id:
            raise MusicGenerationError("Suno API did not return a taskId.")

        return GenerationResult(
            status=GenerationStatus.PROCESSING,
            provider_name=self.provider_name,
            provider_task_id=task_id,
            raw_response=response,
        )

    def refresh(self, generation_request):
        task_id = generation_request.provider_task_id
        if not task_id:
            raise MusicGenerationError("This request does not have a Suno task id yet.")

        response = self._request_json(
            "GET",
            "generate/record-info",
            query={"taskId": task_id},
        )
        if response.get("code") != 200:
            raise MusicGenerationError(response.get("msg", "Failed to fetch Suno task details."))

        data = response.get("data", {})
        suno_status = data.get("status", "PENDING")
        tracks = data.get("response", {}).get("sunoData", [])
        first_track = tracks[0] if tracks else {}
        duration = first_track.get("duration")
        title = first_track.get("title") or generation_request.title
        audio_url = first_track.get("audioUrl") or first_track.get("streamAudioUrl")

        return GenerationResult(
            status=self._map_status(suno_status),
            provider_name=self.provider_name,
            provider_task_id=task_id,
            duration=int(duration) if duration else None,
            title=title,
            audio_url=audio_url,
            error_message=data.get("errorMessage") or "",
            raw_response=response,
        )
