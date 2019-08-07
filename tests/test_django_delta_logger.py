from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.test import TestCase

from django_delta_logger import DeltaEventType
from django_delta_logger.delta_logger import DeltaLogger
from django_delta_logger.models import DeltaEvent

from test_app.models import ModelFoo, ModelBar, BazEnum


class DeltaLoggerBasicUsageTestCase(TestCase):

    def setUp(self):
        with DeltaLogger(ModelFoo, ModelBar):
            foo1 = ModelFoo(foo_int=11)
            foo1.save()  # create
            foo1.foo_char = 'yo'
            foo1.save()  # update
            bar1 = ModelBar(bar_int=10)
            bar1.save()  # create
            bar1.bar_foo = foo1
            bar1.save()  # update
            self.bar = ModelBar(bar_enum=BazEnum.A)
            self.bar.save()  # create
            self.bar.bar_enum = BazEnum.B
            self.bar.bar_bars.add(bar1)
            self.bar.save()  # update
            self.bar.bar_bars.remove(bar1)
            self.bar.save()  # update
            foo1.delete()  # delete (cascading)

    def test_changed_matches_data_keys(self):
        queryset = DeltaEvent.objects.filter(
            event_type__in=[DeltaEventType.CREATED, DeltaEventType.UPDATED]
        )
        for event in queryset:
            data = event.__data_view__()
            self.assertEqual(data['changed'], list(data['data'].keys()))

    def test_deleted_data(self):
        queryset = DeltaEvent.objects.filter(event_type=DeltaEventType.DELETED)
        for event in queryset:
            data = event.__data_view__()
            self.assertIs(None, data['changed'])
            self.assertIs(None, data['data'])

    def test_records_created_events(self):
        self.assertEqual(3, DeltaEvent.objects.filter(event_type=DeltaEventType.CREATED).count())

    def test_records_updated_events(self):
        self.assertEqual(4, DeltaEvent.objects.filter(event_type=DeltaEventType.UPDATED).count())

    def test_records_deleted_events(self):
        self.assertEqual(2, DeltaEvent.objects.filter(event_type=DeltaEventType.DELETED).count())

    def test_created_includes_values(self):
        content_type_bar = ContentType.objects.get_for_model(ModelBar)
        events = DeltaEvent.objects.filter(
            event_sender_type=content_type_bar,
            event_sender_id=self.bar.pk,
            event_type=DeltaEventType.CREATED
        ).all()
        events_data = [event.__data_view__() for event in events]
        self.assertEqual(1, len(events_data),
                         'one created event for this instance')
        event_data = events_data[0]
        self.assertEqual({'bar_id', 'bar_enum'}, set(event_data['changed']),
                         'only changed fields are included')
        self.assertEqual(event_data['data']['bar_enum'], BazEnum.A.value,
                         'the initial value specified is recorded')
        null_keys = [
            key
            for key, value
            in events_data[0]['data'].items()
            if value is None
        ]
        self.assertEqual([], null_keys,
                         'excludes default `None` values on created')

    def test_changed_after_loaded_existing(self):
        with DeltaLogger(ModelBar):
            bar1 = ModelBar.objects.get(pk=self.bar.pk)
            bar1.bar_int = 20
            bar1.save()
        content_type_bar = ContentType.objects.get_for_model(ModelBar)
        event = DeltaEvent.objects.filter(
            event_sender_type=content_type_bar,
            event_sender_id=self.bar.pk,
            event_type=DeltaEventType.UPDATED
        ).order_by('-event_time').first()
        event_data = event.__data_view__()
        self.assertEqual(['bar_int'], event_data['changed'],
                         'update after load only records new changes')

    def test_concurrent(self):
        with DeltaLogger(ModelBar, concurrent=True):
            bar_a = ModelBar.objects.get(pk=self.bar.pk)
            bar_b = ModelBar.objects.get(pk=self.bar.pk)
            bar_a.bar_int = 2
            bar_a.bar_enum = BazEnum.C
            bar_b.bar_int = 3
            self.assertNotEqual(bar_a.bar_int, bar_b.bar_int)
            bar_a.save()
            bar_b.save()
        bar = ModelBar.objects.get(pk=self.bar.pk)
        self.assertEqual(bar.bar_int, bar_b.bar_int)
        self.assertEqual(bar.bar_enum, bar_b.bar_enum)
        content_type_bar = ContentType.objects.get_for_model(ModelBar)
        events = DeltaEvent.objects.filter(
            event_sender_type=content_type_bar,
            event_sender_id=self.bar.pk,
            event_type=DeltaEventType.UPDATED
        ).order_by('-event_time')
        events_data = [e.__data_view__() for e in events]
        self.assertEqual({'bar_int', 'bar_enum'}, set(events_data[0]['changed']),
                         'concurrent update includes concurrent changes')

    def test_get_events_for_model(self):
        q = DeltaEvent.objects.get_events_for_model(ModelBar)
        self.assertIsInstance(q, models.QuerySet)
        self.assertEqual(6, q.count())
        q = DeltaEvent.objects.get_events_for_model(
            ModelBar,
            event_type=DeltaEventType.CREATED
        )
        self.assertEqual(2, q.count())

    def test_get_events_for_instance(self):
        q = DeltaEvent.objects.get_events_for_instance(self.bar)
        self.assertIsInstance(q, models.QuerySet)
        self.assertEqual(3, q.count())
        q = DeltaEvent.objects.get_events_for_instance(
            self.bar,
            event_type=DeltaEventType.CREATED
        )
        self.assertEqual(1, q.count())
