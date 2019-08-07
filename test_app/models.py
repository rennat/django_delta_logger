from enum import Enum

from django.db import models

from django_delta_logger.fields import IntEnumField


BazEnum = Enum('BazEnum', 'A B C')


class ModelFoo(models.Model):
    foo_id = models.AutoField(primary_key=True)
    foo_int = models.IntegerField()
    foo_auto_datetime = models.DateTimeField(auto_now_add=True)
    foo_char = models.CharField(max_length=32, null=True, blank=True)


class ModelBar(models.Model):
    bar_id = models.AutoField(primary_key=True)
    bar_int = models.IntegerField(null=True)
    bar_foo = models.ForeignKey(ModelFoo, null=True, on_delete=models.CASCADE)
    bar_bars = models.ManyToManyField('self', symmetrical=False)
    bar_enum = IntEnumField(BazEnum, null=True)
