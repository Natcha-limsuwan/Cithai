from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, username, name="", google_id=None, email="", **extra_fields):
        user = self.model(username=username, email=email, google_id=google_id, name=name, **extra_fields)
        user.set_password(extra_fields.pop("password", None))
        user.save(using=self._db)
        return user

    def create_superuser(self, username, name="Admin", google_id=None, email="", **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(username, name=name, google_id=google_id, email=email, **extra_fields)


class User(AbstractBaseUser):
    """
    Authenticated person using Cithai.
    Identity is managed entirely via Google OAuth (A-1).
    """
    user_id    = models.AutoField(primary_key=True)
    username   = models.CharField(max_length=150, unique=True)
    google_id  = models.CharField(max_length=255, blank=True, null=True, default=None)
    email      = models.EmailField(unique=True, blank=True, default="")
    name       = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    is_active    = models.BooleanField(default=True)
    is_staff     = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD  = "username"
    REQUIRED_FIELDS = ["name"]

    objects = UserManager()

    class Meta:
        app_label = "core"
        verbose_name = "User"

    def __str__(self):
        return f"{self.name} ({self.username})"

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser