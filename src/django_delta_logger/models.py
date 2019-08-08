import json

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from django_delta_logger import DeltaEventType
from django_delta_logger.fields import IntEnumField


class DeltaEventManager(models.Manager):

    def get_events_for_instance(self, instance, **kwargs):
        content_type = ContentType.objects.get_for_model(instance._meta.model)
        return self.filter(
            event_sender_type=content_type,
            event_sender_id=instance.pk,
            **kwargs
        )
    
    def get_events_for_models(self, *models, **kwargs):
        content_types = [
            ContentType.objects.get_for_model(model)
            for model
            in models
        ]
        return self.filter(event_sender_type__in=content_types, **kwargs)


class DeltaEvent(models.Model):
    objects = DeltaEventManager()

    event_sender_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    event_sender_id = models.PositiveIntegerField()
    event_sender = GenericForeignKey('event_sender_type', 'event_sender_id')
    event_time = models.DateTimeField(auto_now_add=True)
    event_type = IntEnumField(DeltaEventType)
    event_data = models.TextField(blank=True, null=True)

    def __data_view__(self):
        """
        Used when serializing
        """
        if self.event_data:
            data = json.loads(self.event_data)
            keys = list(data.keys())
        else:
            data, keys = None, None
        return {
            'operation': self.event_type.name.lower(),
            'changed': keys,
            'data': data,
            'pk': self.pk,
            'class': self.event_sender_type.model_class()._meta.label,
            'time': self.event_time,
        }

