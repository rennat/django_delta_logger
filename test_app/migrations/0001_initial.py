# Generated by Django 2.2.3 on 2019-07-31 04:20

from django.db import migrations, models
import django.db.models.deletion
import django_delta_logger.fields
import test_app.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ModelFoo',
            fields=[
                ('foo_id', models.AutoField(primary_key=True, serialize=False)),
                ('foo_int', models.IntegerField()),
                ('foo_auto_datetime', models.DateTimeField(auto_now_add=True)),
                ('foo_char', models.CharField(blank=True, max_length=32, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ModelBar',
            fields=[
                ('bar_id', models.AutoField(primary_key=True, serialize=False)),
                ('bar_int', models.IntegerField(null=True)),
                ('bar_enum', django_delta_logger.fields.IntEnumField(test_app.models.BazEnum, choices=[('A', 1), ('B', 2), ('C', 3)], null=True)),
                ('bar_bars', models.ManyToManyField(to='test_app.ModelBar')),
                ('bar_foo', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='test_app.ModelFoo')),
            ],
        ),
    ]
