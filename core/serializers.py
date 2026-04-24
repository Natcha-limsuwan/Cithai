from rest_framework import serializers
from .models import User, Song, MusicGenerationRequest, ShareLink, GenerationStatus, Library


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model  = User
        fields = ["user_id", "email", "name", "google_id", "created_at"]
        read_only_fields = ["user_id", "created_at"]


class SongSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Song
        fields = [
            "song_id", "user", "title", "custom_lyrics", "duration",
            "audio_url", "creation_date", "is_shared", "status",
            "mood", "genre", "occasion", "voice_type",
        ]
        read_only_fields = ["song_id", "creation_date"]

    def validate(self, data):
        # C-2: 20-song limit enforced in model.save(); surfaced here for API errors
        user = data.get("user") or (self.instance.user if self.instance else None)
        if user and not self.instance:
            from .models import Song as SongModel
            if SongModel.objects.filter(user=user).count() >= 20:
                raise serializers.ValidationError(
                    "A user may not own more than 20 songs (C-2)."
                )
        return data


class MusicGenerationRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model  = MusicGenerationRequest
        fields = [
            "request_id", "user", "song", "title", "custom_lyrics",
            "occasion", "genre", "voice_type", "mood", "submitted_at", "is_retry",
            "generation_provider", "provider_task_id", "provider_status_message",
        ]
        read_only_fields = [
            "request_id",
            "submitted_at",
            "song",
            "generation_provider",
            "provider_task_id",
            "provider_status_message",
        ]


class ShareLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model  = ShareLink
        fields = ["link_id", "song", "token", "created_at", "is_active"]
        read_only_fields = ["link_id", "token", "created_at"]

    def validate_song(self, song):
        # C-4: only Complete songs
        if song.status != GenerationStatus.COMPLETE:
            raise serializers.ValidationError(
                "A ShareLink can only be created for a song with status 'Complete' (C-4)."
            )
        return song


class LibrarySerializer(serializers.ModelSerializer):
    song_count = serializers.SerializerMethodField()

    class Meta:
        model  = Library
        fields = ["library_id", "user", "name", "description", "songs", "song_count", "created_at"]
        read_only_fields = ["library_id", "created_at"]

    def get_song_count(self, obj):
        return obj.songs.count()
