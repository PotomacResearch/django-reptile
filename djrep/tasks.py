from huey.contrib.djhuey import db_task
from time import sleep
from djrep.models import ReptileTraining
from django.utils.timezone import now


@db_task()
def run_dummy_task(seconds, name, pk):
    training_obj = ReptileTraining.objects.get(pk=pk)

    training_obj.started = now()
    for i in range(seconds):
        print(f'-- {name} waited {i} seconds --')
        sleep(1)


    training_obj.completed = now()
    training_obj.save()

