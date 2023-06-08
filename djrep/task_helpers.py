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
    training_obj.started = now()
    training_obj.save()

    return (training_obj.name, training_obj.type, training_obj.params)


@manage_db_connection
def complete_training(reptile_training_id: int) -> None:
    """
    Marks the training process complete
    """
    training_obj = ReptileTraining.objects.get(pk=reptile_training_id)
    training_obj.completed = now()
    training_obj.save()
