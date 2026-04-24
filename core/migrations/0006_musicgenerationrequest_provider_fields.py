from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0005_alter_user_username"),
    ]

    operations = [
        migrations.AddField(
            model_name="musicgenerationrequest",
            name="generation_provider",
            field=models.CharField(default="mock", max_length=20),
        ),
        migrations.AddField(
            model_name="musicgenerationrequest",
            name="provider_status_message",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
        migrations.AddField(
            model_name="musicgenerationrequest",
            name="provider_task_id",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
    ]
