# Django Delta Logger

A django app that provides a model class that records changes in django models.


## Installation

### Get the Package

```
pip install django_delta_logger
```

### Update the Django Settings

Add `django_delta_logger` to the `INSTALLED_APPS` list.

```
INSTALLED_APPS=[
    # ...
    'django_delta_logger',
    # ...
]
```

Make sure `JSON_ENCODER` is set in the django settings. A reasonable default is provided and is directly importable into an existing settings file.

```
from django_delta_logger.settings import JSON_ENCODER
```

## Usage

Django_delta_logger's primary API is a context manager:

```
from django_delta_logger.delta_logger import DeltaLogger

with DeltaLogger(SomeDjangoModel, SomeOtherDjangoModel):
    foo = SomeDjangoModel(name='foo')
    foo.save()
```

## Log Results

Access the history of a model instance from the `DeltaEvent` model.

```
from django_delta_logger.models import DeltaEvent

instance = SomeModel.objects.get(pk=1)
events = DeltaEvent.objects.get_for_instance(instance).all()

for event in events:
    print(event.event_time, event.event_type, event.event_data)
```

```
from django_delta_logger.models import DeltaEvent

events = DeltaEvent.objects.get_for_model(SomeDjangoModel).all()

for event in events:
    print(event.event_time, event.event_type, event.event_data)
```

### The Risks of Concurrency

Tracking the `dirtyness` of a model instance field is performant but can lead to inaccurate log data when one
model instance is edited in multiple threads/processes/servers.

When data accuracy in a concurrent environment is worth the performance cost of a fetch-before-write:

```
from django_delta_logger.delta_logger import DeltaLogger

with DeltaLogger(SomeDjangoModel, concurrent=True):
    foo = SomeDjangoModel(name='foo')
    foo.save()
```

## Test Suite

`python setup.py test`


## License

This software is published under the MIT License. See the `LICENSE` file
for details.
