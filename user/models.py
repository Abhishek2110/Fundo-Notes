from django.db import models

# Create your models here.
class User(models.Model):
    username = models.CharField(max_length=50, null=False, unique=True)
    email = models.EmailField(null=False)
    password = models.CharField(max_length=250, null=False)
    is_verified = models.BooleanField(default=False)