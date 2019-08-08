from django.conf import settings
from django.utils.module_loading import import_string


JsonEncoder = import_string(settings.JSON_ENCODER)
