
import json

from django.conf import settings
from django.db.models import signals
from django.db.models.fields import NOT_PROVIDED
from django.db.transaction import atomic
from django.utils.module_loading import import_string

from django_delta_logger import DOES_NOT_EXIST
from django_delta_logger.models import DeltaEvent, DeltaEventType


JsonEncoder = import_string(settings.JSON_ENCODER)


class Cache:
    """
    Functions for keeping and comparing dirty states on django models
    """

    @classmethod
    def update(cls, instance, state=None):
        instance._delta_logger_cache = state or cls.get_current(instance)

    @classmethod
    def compare_and_update(cls, instance):
        cached = getattr(instance, '_delta_logger_cache', cls.get_defaults(instance._meta.model))
        current = cls.get_current(instance)
        delta = cls.get_delta(cached, current)
        cls.update(instance, state=current)
        return delta

    @staticmethod
    def get_delta(a, b):
        return {
            key: new
            for key, old, new
            in (
                (
                    key,
                    a.get(key, DOES_NOT_EXIST),
                    b.get(key, DOES_NOT_EXIST)
                )
                for key
                in set(a.keys()).union(b.keys())
            )
            if (
                old == DOES_NOT_EXIST
                or new == DOES_NOT_EXIST
                or old != new
            )
        }

    @staticmethod
    def get_current(instance):
        return {
            f.attname: getattr(instance, f.attname)
            for f
            in instance._meta.get_fields()
            if hasattr(f, 'attname')
            and getattr(f, 'concrete', False)
            and not getattr(f, 'many_to_many', False)
        }
    
    @staticmethod
    def get_defaults(model):
        return {
            f.attname: None if f.default is NOT_PROVIDED else f.default
            for f
            in model._meta.get_fields()
            if hasattr(f, 'attname')
            and getattr(f, 'concrete', False)
            and not getattr(f, 'many_to_many', False)
        }


class DeltaLogger:
    """
    ContextManager that records changes to the specified django models while active
    """

    def __init__(self, *models, concurrent=False):
        self._models = models
        self._concurrent = concurrent

    def __enter__(self):
        signals.post_init.connect(self.handle_post_init, dispatch_uid='django_delta_logger.post_init')
        signals.pre_save.connect(self.handle_pre_save, dispatch_uid='django_delta_logger.pre_save')
        signals.post_save.connect(self.handle_post_save, dispatch_uid='django_delta_logger.post_save')
        signals.pre_delete.connect(self.handle_pre_delete, dispatch_uid='django_delta_logger.pre_delete')

    def __exit__(self, exc_type, exc_value, traceback):
        signals.post_init.disconnect(self.handle_post_init, dispatch_uid='django_delta_logger.post_init')
        signals.pre_save.disconnect(self.handle_pre_save, dispatch_uid='django_delta_logger.pre_save')
        signals.post_save.disconnect(self.handle_post_save, dispatch_uid='django_delta_logger.post_save')
        signals.pre_delete.disconnect(self.handle_pre_delete, dispatch_uid='django_delta_logger.pre_delete')

    def handle_post_init(self, sender, **kwargs):
        if sender in self._models:
            instance = kwargs.get('instance')
            Cache.update(instance)

    def handle_pre_save(self, sender, **kwargs):
        if (
            sender in self._models
            and self._concurrent
        ):
            instance = kwargs.get('instance')
            existing = instance._meta.model.objects.get(pk=instance.pk)
            Cache.update(instance, state=Cache.get_current(existing))
    
    def handle_post_save(self, sender, **kwargs):
        if sender in self._models:
            instance = kwargs.get('instance')
            created = kwargs.get('created')
            if created:
                Cache.update(instance, state=Cache.get_defaults(instance._meta.model))
            delta = Cache.compare_and_update(instance)
            event = DeltaEvent(
                event_sender=instance,
                event_type=DeltaEventType.CREATED if created else DeltaEventType.UPDATED,
                event_data=json.dumps(delta, cls=JsonEncoder)
            )
            event.save()
    
    def handle_pre_delete(self, sender, **kwargs):
        if sender in self._models:
            instance = kwargs.get('instance')
            event = DeltaEvent(
                event_sender=instance,
                event_type=DeltaEventType.DELETED
            )
            event.save()
