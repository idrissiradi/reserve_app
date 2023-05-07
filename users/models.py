from django.db import models
from django.contrib.auth.models import AbstractUser

from .managers import NewUserManager


class User(AbstractUser):
    username = None
    email = models.EmailField(("email address"), unique=True)
    admin = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = NewUserManager()

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"
