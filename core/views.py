import mimetypes
from os.path import basename
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urlparse
from urllib.request import Request, urlopen

from django.http import FileResponse
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status, viewsets
from .models import User, Song, MusicGenerationRequest, ShareLink, Library
from .serializers import (
    UserSerializer, SongSerializer,
    MusicGenerationRequestSerializer, ShareLinkSerializer, LibrarySerializer,
)
from django.conf import settings

from .services.music_generation import MusicGenerationService
from .services.music_generation.base import MusicGenerationError


class UserViewSet(viewsets.ModelViewSet):
    """CRUD for User domain entity."""
    queryset         = User.objects.all().order_by("-created_at")
    serializer_class = UserSerializer
    permission_classes = [AllowAny]   # relaxed for demo; lock down in production


class SongViewSet(viewsets.ModelViewSet):
    """
    CRUD for Song domain entity.
    Enforces C-2 (20-song limit) via serializer + model.
    """
    queryset         = Song.objects.select_related("user").all()
    serializer_class = SongSerializer
    permission_classes = [AllowAny]

    @action(detail=True, methods=["get"])
    def download(self, request, pk=None):
        song = self.get_object()
        if not song.audio_url:
            return Response(
                {"detail": "No audio file available for this song."},
                status=status.HTTP_404_NOT_FOUND,
            )

        filename = self._build_download_filename(song)

        try:
            remote_request = Request(
                song.audio_url,
                headers={"User-Agent": "CithaiDownloader/1.0"},
            )
            remote_file = urlopen(remote_request, timeout=30)
        except (HTTPError, URLError, ValueError):
            return Response(
                {"detail": "Could not fetch the audio file for download."},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        content_type = remote_file.headers.get_content_type()
        if not content_type or content_type == "application/octet-stream":
            guessed_type, _ = mimetypes.guess_type(filename)
            content_type = guessed_type or "application/octet-stream"

        return FileResponse(
            remote_file,
            as_attachment=True,
            filename=filename,
            content_type=content_type,
        )

    def _build_download_filename(self, song):
        slug = "".join(
            c.lower() if c.isalnum() else "-"
            for c in (song.title or "song").strip()
        ).strip("-")
        while "--" in slug:
            slug = slug.replace("--", "-")
        slug = slug or "song"

        path = urlparse(song.audio_url).path
        extension = basename(unquote(path)).rsplit(".", 1)[-1].lower() if "." in basename(unquote(path)) else "mp3"
        return f"{slug}.{extension}"


class MusicGenerationRequestViewSet(viewsets.ModelViewSet):
    """CRUD for MusicGenerationRequest domain entity."""
    queryset         = MusicGenerationRequest.objects.select_related("user", "song").all()
    serializer_class = MusicGenerationRequestSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        generation_request = serializer.save()
        generation_request.generation_provider = settings.GENERATOR_STRATEGY
        generation_request.save(update_fields=["generation_provider"])

        try:
            MusicGenerationService().submit_request(generation_request)
        except MusicGenerationError as exc:
            generation_request.generation_provider = settings.GENERATOR_STRATEGY
            generation_request.provider_status_message = str(exc)
            generation_request.save(
                update_fields=["generation_provider", "provider_status_message"]
            )

        response_serializer = self.get_serializer(generation_request)
        headers = self.get_success_headers(response_serializer.data)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=["post"])
    def refresh_generation(self, request, pk=None):
        generation_request = self.get_object()
        provider = generation_request.generation_provider or "mock"

        try:
            from .services.music_generation.factory import get_music_generation_strategy
            strategy = get_music_generation_strategy(provider)
            MusicGenerationService(strategy=strategy).refresh_request(generation_request)
        except MusicGenerationError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(self.get_serializer(generation_request).data)


class ShareLinkViewSet(viewsets.ModelViewSet):
    """
    CRUD for ShareLink domain entity.
    Enforces C-4 (only Complete songs can have a ShareLink) via serializer + model.
    """
    queryset         = ShareLink.objects.select_related("song").all()
    serializer_class = ShareLinkSerializer
    permission_classes = [AllowAny]


class LibraryViewSet(viewsets.ModelViewSet):
    """CRUD for Library — user-defined collections of Songs."""
    queryset           = Library.objects.prefetch_related("songs").select_related("user").all()
    serializer_class   = LibrarySerializer
    permission_classes = [AllowAny]

    @action(detail=True, methods=["post"])
    def add_song(self, request, pk=None):
        library = self.get_object()
        song_id = request.data.get("song_id")
        try:
            song = Song.objects.get(song_id=song_id)
            library.songs.add(song)
            return Response(self.get_serializer(library).data)
        except Song.DoesNotExist:
            return Response({"detail": "Song not found."}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=["post"])
    def remove_song(self, request, pk=None):
        library = self.get_object()
        song_id = request.data.get("song_id")
        try:
            song = Song.objects.get(song_id=song_id)
            library.songs.remove(song)
            return Response(self.get_serializer(library).data)
        except Song.DoesNotExist:
            return Response({"detail": "Song not found."}, status=status.HTTP_404_NOT_FOUND)
