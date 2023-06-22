from pathlib import Path

from django.db import models
from django.conf import settings

from djrep.types import ReptileTypes


class ReptileTraining(models.Model):
    name = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)
    started = models.DateTimeField(null=True)
    completed = models.DateTimeField(null=True)
    params = models.JSONField(blank=True, default=dict)
    type = models.CharField(max_length=20,
                            choices=ReptileTypes.sorted_choices())
    data_file = models.FileField(blank=True, null=True,
                                 upload_to='training_sources')
    status = models.CharField(max_length=100, default="Waiting to start")
    status_timestamp = models.DateTimeField(null=True)

    user = models.ForeignKey(
        "account.User",
        models.CASCADE,
        related_name="trainings",
    )

    def __str__(self):
        return self.name

    @staticmethod
    def get_base_save_path(reptile_training_id: int) -> Path:
        return Path(settings.MEDIA_ROOT) / f'{reptile_training_id}'