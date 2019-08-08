from django.http import JsonResponse

from django_delta_logger.delta_logger import DeltaLogger
from django_delta_logger.models import DeltaEvent

from example_django_project.serialization import JsonEncoder
from example_app.models import User, Organization


def example_action_view(request):
    with DeltaLogger(User, Organization):
        user = User(first_name='x')
        user.save()
        user.last_name = 'y'
        user.save()
        org = Organization(name='A', slug='a')
        org.save()
        org.name = 'B'
        org.save()
        org.delete()
    return JsonResponse(
        {'success': True},
        encoder=JsonEncoder,
        safe=False
    )


def example_history_view(request):
    return JsonResponse(
        list(DeltaEvent.objects.get_events_for_models(User, Organization).all()),
        encoder=JsonEncoder,
        safe=False,
        json_dumps_params={
            'indent': 2,
            'sort_keys': True,
        }
    )
