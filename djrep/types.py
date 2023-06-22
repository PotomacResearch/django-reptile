from django.db import models

class ReptileTypes(models.TextChoices):
    SINE_EXAMPLE = "Sine", "Sine Example"


    @classmethod
    def sorted_choices(cls):
        return sorted(cls.choices, key=lambda k: k[1].lower())