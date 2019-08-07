__VERSION__ = '0.1.0'


from enum import Enum
import json

from django.core.exceptions import ImproperlyConfigured


default_app_config = 'django_delta_logger.apps.DjangoDeltaLoggerConfig'


DOES_NOT_EXIST = object()
DeltaEventType = Enum('DeltaEventType', 'CREATED UPDATED DELETED')
