from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.views import (
    UserViewSet, SongViewSet,
    MusicGenerationRequestViewSet, ShareLinkViewSet,
)

router = DefaultRouter()
router.register(r"users",    UserViewSet,                   basename="user")
router.register(r"songs",    SongViewSet,                   basename="song")
router.register(r"requests", MusicGenerationRequestViewSet, basename="request")
router.register(r"shares",   ShareLinkViewSet,              basename="sharelink")

urlpatterns = [
    path("admin/",  admin.site.urls),
    path("api/",    include(router.urls)),
    path("api-auth/", include("rest_framework.urls")),
]
