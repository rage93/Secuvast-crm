import json

from django.db import models
from django.contrib.auth.models import User
from django_quill.fields import QuillField

from apps.companies.models import CompanyScopedModel


ROLE_CHOICES = (
    ("admin", "Admin"),
    ("user", "User"),
    ("suspended", "Suspended"),
)


def avatar_with_id(instance, filename):
    return f"{instance.user.id}/avatar/{filename}"


def convert_to_quill():
    return json.dumps({"delta": "", "html": "Write something #cool about you."})


class Profile(CompanyScopedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="user")
    full_name = models.CharField(max_length=255, null=True, blank=True)
    country = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    zip_code = models.CharField(max_length=255, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=255, null=True, blank=True)
    position = models.CharField(max_length=100, null=True, blank=True)
    avatar = models.ImageField(upload_to=avatar_with_id, null=True, blank=True)
    bio = QuillField(default=convert_to_quill())
    dark_mode = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.user.username

