import os
from io import StringIO
from pathlib import Path

from django.db import models
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.validators import MinValueValidator
import csv


class Dataset(models.Model):
    name = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)
    params = models.JSONField(blank=True, default=dict)
    original_filename = models.CharField()
    members = models.IntegerField(validators=[MinValueValidator(1)],
                                  verbose_name="Number of Library Members")
    inputs = models.IntegerField(validators=[MinValueValidator(1)],
                                 verbose_name="Number of Inputs")
    outputs = models.IntegerField(validators=[MinValueValidator(0)],
                                  verbose_name="Number of Outputs")
    deleted = models.BooleanField(default=False)

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

    def get_source_csv_path(self) -> Path:
        return self._get_base_path() / 'data.csv'

    @staticmethod
    def check_data_file(file_obj: StringIO,
                        n_members: int, n_inputs: int, n_outputs: int) -> bool:
        """
        Check that a given data file passes sanity checks to be a valid source
        Raises an Exception if doesn't pass
        """
        n_cols = n_members * (n_inputs + n_outputs)

        # Check file contents
        reader = csv.reader(file_obj)
        next(reader) # skip the first row
        for row in reader:
            row_len = len([float(f) for f in row])
            if  row_len != n_cols:
                raise ValueError(
                    f'Bad number of rows: {row_len} (should be {n_cols})'
                )

        return True


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
