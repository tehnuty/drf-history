# Third-Party Imports
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from track_actions.constants import TABLES
from track_actions.models import History
# App Imports
from track_actions.requestMiddleware import RequestMiddleware


@receiver(post_save)
@receiver(post_delete)
def track_application_track_actions(sender, instance, **kwargs):
    current_request = RequestMiddleware.get_request_data()[1]
    if (
        sender._meta.db_table not in TABLES
        and hasattr(current_request, "user")
        and hasattr(instance, "id")
    ):
        data = instance.__dict__.copy()
        data.__delitem__("_state")
        try:
            history = History(
                table_name=str(instance._meta.db_table),
                user=current_request.user,
                instance_id=instance.id,
                action=current_request.method,
                request_data=RequestMiddleware.get_request_data()[0],
                response_data=data,
            )
            history.save()
        except ValueError:
            pass