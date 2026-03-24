from django.db import models


class Mood(models.TextChoices):
    HAPPY     = "Happy",      "Happy"
    SAD       = "Sad",        "Sad"
    ROMANTIC  = "Romantic",   "Romantic"
    ENERGETIC = "Energetic",  "Energetic"
    CALM      = "Calm",       "Calm"


class Genre(models.TextChoices):
    POP       = "Pop",       "Pop"
    ROCK      = "Rock",      "Rock"
    JAZZ      = "Jazz",      "Jazz"
    CLASSICAL = "Classical", "Classical"
    HIPHOP    = "HipHop",    "HipHop"


class Occasion(models.TextChoices):
    BIRTHDAY    = "Birthday",    "Birthday"
    WEDDING     = "Wedding",     "Wedding"
    GRADUATION  = "Graduation",  "Graduation"
    ANNIVERSARY = "Anniversary", "Anniversary"
    CUSTOM      = "Custom",      "Custom"


class VoiceType(models.TextChoices):
    MALE         = "Male",         "Male"
    FEMALE       = "Female",       "Female"
    CHILD        = "Child",        "Child"
    CHOIR        = "Choir",        "Choir"
    INSTRUMENTAL = "Instrumental", "Instrumental"
    DUET         = "Duet",         "Duet"


class GenerationStatus(models.TextChoices):
    PENDING    = "Pending",    "Pending"
    PROCESSING = "Processing", "Processing"
    COMPLETE   = "Complete",   "Complete"
    FAILED     = "Failed",     "Failed"
    