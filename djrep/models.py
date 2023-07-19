import os
from pathlib import Path

from django.db import models
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile


class Dataset(models.Model):
    name = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)
    params = models.JSONField(blank=True, default=dict)
    original_filename = models.CharField()

    user = models.ForeignKey(
        "account.User",
        models.CASCADE,
        related_name="datasets",
    )

    def __str__(self):
        return self.name

    def _get_base_path(self) -> Path:
        return Path(settings.MEDIA_ROOT) / 'datasets' / f'{self.id}'

    def save_source_csv(self, csv_file: InMemoryUploadedFile):
        save_path = self._get_base_path()
        os.makedirs(save_path, exist_ok=True)
        with open(save_path / 'data.csv', 'wb') as f:
            for chunk in csv_file.chunks():
                f.write(chunk)


class Reptile(models.Model):
    name = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)
    started = models.DateTimeField(null=True)
    completed = models.DateTimeField(null=True)
    params = models.JSONField(blank=True, default=dict)
    status = models.CharField(max_length=100, default="Waiting to start")
    status_timestamp = models.DateTimeField(null=True)

    dataset = models.ForeignKey(
        "djrep.Dataset",
        models.CASCADE,
        related_name="reptiles"
    )
    user = models.ForeignKey(
        "account.User",
        models.CASCADE,
        related_name="reptiles",
    )

    def __str__(self):
        return self.name

    @staticmethod
    def get_base_save_path(reptile_id: int) -> Path:
        return Path(settings.MEDIA_ROOT) / f'{reptile_id}'
