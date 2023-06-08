from huey.contrib.djhuey import task

from reptile import toysystems

from djrep.task_helpers import start_training,complete_training


@task()
def run_dummy_task(reptile_training_id):
    task_name = start_training(reptile_training_id)

    library = toysystems.sine_example()
    print(f'{task_name} completed training sine: {library}')

    complete_training(reptile_training_id)
