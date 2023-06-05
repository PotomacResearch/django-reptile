from django.db import models


class ReptileTraining(models.Model):
    name = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)
    started = models.DateTimeField(null=True)
    completed = models.DateTimeField(null=True)

    user = models.ForeignKey(
        "account.User",
        models.CASCADE,
        related_name="trainings",
    )


    def __str__(self):
        return self.name
