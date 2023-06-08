from django.db import models
from djrep.types import ReptileTypes


class ReptileTraining(models.Model):
    name = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)
    started = models.DateTimeField(null=True)
    completed = models.DateTimeField(null=True)
    params = models.JSONField(blank=True, default=dict)
    type = models.CharField(max_length=20,
                            choices=ReptileTypes.sorted_choices())

    user = models.ForeignKey(
        "account.User",
        models.CASCADE,
        related_name="trainings",
    )


    def __str__(self):
        return self.name
