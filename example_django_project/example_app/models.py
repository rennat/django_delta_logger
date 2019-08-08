from django.db import models

class User(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(max_length=100, blank=True)

class Organization(models.Model):
    name = models.CharField(max_length=100)
    slug = models.CharField(max_length=100, unique=True, db_index=True)
