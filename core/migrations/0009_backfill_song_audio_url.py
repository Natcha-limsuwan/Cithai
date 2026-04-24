from django.db import migrations

MOCK_AUDIO_URL = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"


def backfill_audio_url(apps, schema_editor):
    Song = apps.get_model("core", "Song")
    Song.objects.filter(audio_url__isnull=True).update(audio_url=MOCK_AUDIO_URL)


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0008_add_song_audio_url"),
    ]

    operations = [
        migrations.RunPython(backfill_audio_url, migrations.RunPython.noop),
    ]
