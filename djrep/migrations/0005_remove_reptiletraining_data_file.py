# Generated by Django 4.2.1 on 2023-06-23 17:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('djrep', '0004_reptiletraining_status_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reptiletraining',
            name='data_file',
        ),
    ]
