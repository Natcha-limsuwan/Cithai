from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import User, Song, MusicGenerationRequest, ShareLink
from .serializers import (
    UserSerializer, SongSerializer,
    MusicGenerationRequestSerializer, ShareLinkSerializer,
)


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


class ShareLinkViewSet(viewsets.ModelViewSet):
    """
    CRUD for ShareLink domain entity.
    Enforces C-4 (only Complete songs can have a ShareLink) via serializer + model.
    """
    queryset         = ShareLink.objects.select_related("song").all()
    serializer_class = ShareLinkSerializer
    permission_classes = [AllowAny]
