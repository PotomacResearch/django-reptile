from huey.contrib.djhuey import task

from djrep.task_helpers import start_training,complete_training


@task()
def run_dummy_task(reptile_training_id):
    task_name = start_training(reptile_training_id)

    # Import here so that Django doesn't require running reptile to serve
    #    the website
    from reptile import toysystems
    library = toysystems.sine_example()
    print(f'{task_name} completed training sine: {library}')

    complete_training(reptile_training_id)
