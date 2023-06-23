from functools import wraps
from django.db import close_old_connections, connection
from djrep.models import ReptileTraining
from django.utils.timezone import now
from typing import Tuple, Dict


def manage_db_connection(func):
    """
    Wrapper around a function requiring a DB connection
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            close_old_connections()
            return func(*args, **kwargs)
        finally:
            connection.close()

    return wrapper


@manage_db_connection
def start_training(reptile_training_id: int
                   ) -> Tuple[str, str, Dict[str, str]]:
    """
    Starts the training process and sets the started field
    """
    training_obj = ReptileTraining.objects.get(pk=reptile_training_id)
    training_obj.status = "Started task"
    training_obj.status_timestamp = now()
    training_obj.started = now()
    training_obj.save()

    return (training_obj.name, training_obj.type,
            training_obj.params['library'],
            training_obj.params['esn'],
            training_obj.params['autoencoder'],
            )



@manage_db_connection
def update_status(reptile_training_id: int, status: str) -> None:
    """
    Updates the DB with the status of the training

    status has to be less than the field length of ReptileTraining.status,
        which is currently 100 characters
    """
    training_obj = ReptileTraining.objects.get(pk=reptile_training_id)
    training_obj.status = status[:100]
    training_obj.status_timestamp = now()
    training_obj.save()


@manage_db_connection
def save_training(reptile_training_id: int) -> None:
    """
    Marks the training process complete and save the results
    """
    training_obj = ReptileTraining.objects.get(pk=reptile_training_id)
    training_obj.status = "Completed"
    training_obj.status_timestamp = now()
    training_obj.completed = now()
    training_obj.save()
