import logging

from django.db.models import fields


class IntEnumField(fields.IntegerField):

    description = 'Represents an IntEnum as a model field'

    def __init__(self, enum, *args, **kwargs):
        for item in enum:
            assert isinstance(item.value, int), "IntEnumField only supports integer values in Enums"
        self.enum = enum
        super().__init__(
            *args,
            **{
                'choices': self.get_choices_from_enum(self.enum),
                **kwargs
            }
        )

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        return name, path, [self.enum] + args, kwargs

    def _convert_value_to_enum(self, value):
        if value is not None:
            value_map = self.get_enums_by_value_map(self.enum)
            if value in value_map:
                return value_map[value]
            else:
                logging.WARN('unexpected enum value: {} not found in enum {}'.format(value, self.enum))
                return value
        else:
            return None

    def from_db_value(self, value, expression, connection):
        return self._convert_value_to_enum(value)

    def to_python(self, value):
        if isinstance(value, self.enum):
            return value
        else:
            return self._convert_value_to_enum(value)

    def get_prep_value(self, value):
        if value is None:
            return None
        elif isinstance(value, int):
            return value
        elif hasattr(value, 'value'):
            return value.value
        else:
            raise TypeError('Unable to coerce {} to integer'.format(value))

    def get_db_prep_value(self, value, connection, prepared=False):
        return self.get_prep_value(value)

    @staticmethod
    def get_choices_from_enum(enum):
        return tuple(
            (item.name, item.value)
            for item in enum
        )

    @staticmethod
    def get_enums_by_value_map(enum):
        return {
            item.value: item
            for item in enum
        }
