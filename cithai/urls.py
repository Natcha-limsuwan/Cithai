from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.views import (
    UserViewSet, SongViewSet,
    MusicGenerationRequestViewSet, ShareLinkViewSet, LibraryViewSet,
)
from core.frontend_views import index, library, create_song, song_detail, libraries_list, library_detail_page
from core.oauth_views import google_login, google_callback

router = DefaultRouter()
router.register(r"users",     UserViewSet,                   basename="user")
router.register(r"songs",     SongViewSet,                   basename="song")
router.register(r"requests",  MusicGenerationRequestViewSet, basename="request")
router.register(r"shares",    ShareLinkViewSet,              basename="sharelink")
router.register(r"libraries", LibraryViewSet,                basename="library")

urlpatterns = [
    # Frontend
    path("",                           index,               name="index"),
    path("library/",                   library,             name="library"),
    path("create/",                    create_song,         name="create_song"),
    path("songs/<int:song_id>/",       song_detail,         name="song_detail"),
    path("libraries/",                 libraries_list,      name="libraries_list"),
    path("libraries/<int:library_id>/", library_detail_page, name="library_detail_page"),

    # Google OAuth
    path("auth/google/",              google_login,    name="google_login"),
    path("auth/google/callback/",     google_callback, name="google_callback"),

    # API & Admin
    path("admin/",    admin.site.urls),
    path("api/",      include(router.urls)),
    path("api-auth/", include("rest_framework.urls")),
]
