from enum import Enum

from django.core.serializers.json import DjangoJSONEncoder


class JsonEncoder(DjangoJSONEncoder):
    def default(self, o):
        if hasattr(o, '__data_view__') and callable(o.__data_view__):
            return o.__data_view__()
        if isinstance(o, Enum):
            return o.value
        else:
            return super().default(o)
