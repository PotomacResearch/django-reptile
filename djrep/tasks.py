from time import sleep
from huey.contrib.djhuey import task

from djrep.task_helpers import start_training,complete_training


@task()
def run_dummy_task(reptile_training_id):
    task_name = start_training(reptile_training_id)

    for i in range(10):
        print(f'-- {task_name} waited {i} seconds --')
        sleep(1)

    complete_training(reptile_training_id)
