from django.db import models
from user.models import User

# Create your models here.
class Notes(models.Model):
    title = models.CharField(max_length = 255, null = True)
    description = models.TextField(null = True)
    color = models.CharField(max_length=50, null = True)
    reminder = models.DateTimeField(null = True)
    is_archive = models.BooleanField(default = False)
    is_trash = models.BooleanField(default = False)
    user = models.ForeignKey(User, on_delete = models.CASCADE)

    class Meta:
        db_table = 'notes'

    def __str__(self) -> str:
        return f'{self.title}'