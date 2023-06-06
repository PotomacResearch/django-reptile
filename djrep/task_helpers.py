from functools import wraps
from django.db import close_old_connections, connection
from djrep.models import ReptileTraining
from django.utils.timezone import now


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
def start_training(reptile_training_id):
    """
    Starts the training process and sets the started field
    """
    training_obj = ReptileTraining.objects.get(pk=reptile_training_id)
    training_obj.started = now()
    training_obj.save()

    return training_obj.name


@manage_db_connection
def complete_training(reptile_training_id):
    """
    Marks the training process complete
    """
    training_obj = ReptileTraining.objects.get(pk=reptile_training_id)
    training_obj.completed = now()
    training_obj.save()
