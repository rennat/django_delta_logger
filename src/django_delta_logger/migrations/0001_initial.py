# Generated by Django 2.2.3 on 2019-07-31 01:53

from django.db import migrations, models
import django.db.models.deletion
import django_delta_logger
import django_delta_logger.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeltaEvent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_sender_id', models.PositiveIntegerField()),
                ('event_time', models.DateTimeField(auto_now_add=True)),
                ('event_type', django_delta_logger.fields.IntEnumField(django_delta_logger.DeltaEventType, choices=[('CREATED', 1), ('UPDATED', 2), ('DELETED', 3)])),
                ('event_data', models.TextField(blank=True, null=True)),
                ('event_sender_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
            ],
        ),
    ]
