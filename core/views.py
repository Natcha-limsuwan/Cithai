from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
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
