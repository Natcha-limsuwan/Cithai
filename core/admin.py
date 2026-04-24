from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Song, MusicGenerationRequest, ShareLink, Library


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display   = ("user_id", "email", "name", "google_id", "created_at", "is_staff")
    search_fields  = ("email", "name", "google_id")
    ordering       = ("-created_at",)
    readonly_fields = ("created_at",)
    list_filter    = ("is_active", "is_staff", "is_superuser")

    fieldsets = (
        (None,          {"fields": ("email", "google_id", "name")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser")}),
        ("Timestamps",  {"fields": ("created_at",)}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields":  ("email", "google_id", "name", "is_staff", "is_superuser"),
        }),
    )


@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    list_display   = ("song_id", "title", "user", "status", "genre", "mood",
                      "occasion", "voice_type", "duration", "is_shared", "creation_date")
    list_filter    = ("status", "genre", "mood", "occasion", "voice_type", "is_shared")
    search_fields  = ("title", "user__email", "user__name")
    ordering       = ("-creation_date",)
    readonly_fields = ("creation_date",)

    fieldsets = (
        ("Identification", {"fields": ("user", "title")}),
        ("Parameters",     {"fields": ("mood", "genre", "occasion", "voice_type")}),
        ("Content",        {"fields": ("custom_lyrics", "duration")}),
        ("Status",         {"fields": ("status", "is_shared")}),
        ("Timestamps",     {"fields": ("creation_date",)}),
    )


@admin.register(MusicGenerationRequest)
class MusicGenerationRequestAdmin(admin.ModelAdmin):
    list_display   = (
        "request_id", "title", "user", "song", "generation_provider",
        "provider_task_id", "is_retry", "submitted_at"
    )
    list_filter    = ("is_retry", "generation_provider", "genre", "mood", "occasion", "voice_type")
    search_fields  = ("title", "user__email")
    readonly_fields = ("submitted_at", "generation_provider", "provider_task_id", "provider_status_message")

    fieldsets = (
        ("Identification", {"fields": ("user", "song", "is_retry")}),
        ("Input Data",     {"fields": ("title", "mood", "genre", "occasion", "voice_type", "custom_lyrics")}),
        ("Provider",       {"fields": ("generation_provider", "provider_task_id", "provider_status_message")}),
        ("Timestamps",     {"fields": ("submitted_at",)}),
    )


@admin.register(ShareLink)
class ShareLinkAdmin(admin.ModelAdmin):
    list_display   = ("link_id", "song", "token", "is_active", "created_at")
    list_filter    = ("is_active",)
    search_fields  = ("song__title", "token")
    readonly_fields = ("token", "created_at")


@admin.register(Library)
class LibraryAdmin(admin.ModelAdmin):
    list_display   = ("library_id", "name", "user", "song_count", "created_at")
    search_fields  = ("name", "user__email")
    readonly_fields = ("created_at",)
    filter_horizontal = ("songs",)

    def song_count(self, obj):
        return obj.songs.count()
    song_count.short_description = "Songs"
