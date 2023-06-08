from huey.contrib.djhuey import task

from djrep.task_helpers import start_training,complete_training
from djrep.types import ReptileTypes


@task()
def run_dummy_task(reptile_training_id: int) -> None:
    task_name, task_type, task_params = start_training(reptile_training_id)

    # Import here so that Django doesn't require running reptile to serve
    #    the website
    from reptile import toysystems
    if task_type == ReptileTypes.SINE_EXAMPLE:
        library = toysystems.sine_example(**task_params)
    else:
        raise NotImplementedError(f'Type not implemented: {type}')

    print(f'{task_name} completed training {type}: {library}')

    complete_training(reptile_training_id)
