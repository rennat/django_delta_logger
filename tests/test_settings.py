import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'tests', 'db.sqlite3'),
    }
}
INSTALLED_APPS = (
    'django.contrib.contenttypes',
    'django_delta_logger',
    'test_app',
)
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True
SECRET_KEY = 'test-key'

# use default settings for the delta logger app
from django_delta_logger.settings import JSON_ENCODER
