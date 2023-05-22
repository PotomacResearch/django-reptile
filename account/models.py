from django.db.models.base import Model
from django.db import models
from django.contrib.auth.models import AbstractUser


class Account(Model):
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class User(AbstractUser):
    account = models.ForeignKey(
        "account.Account",
        models.CASCADE,
        related_name="users",
        null=True,   # For superusers only
    )
