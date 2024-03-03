from django.db import models
from user.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_celery_beat.models import PeriodicTask, CrontabSchedule
from django.conf import settings
import json
from datetime import timedelta, datetime
from django.utils import timezone

class Collaborator(models.Model):
    note = models.ForeignKey("Notes", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    access_type = models.CharField(max_length=20, default="read-only")
    
    class Meta:
        db_table = 'collaborators'

# Create your models here.
class Notes(models.Model):
    title = models.CharField(max_length = 255, null = True)
    description = models.TextField(null = True)
    color = models.CharField(max_length=50, null = True)
    reminder = models.DateTimeField(null = True)
    is_archive = models.BooleanField(default = False)
    is_trash = models.BooleanField(default = False)
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    collaborators = models.ManyToManyField(User, related_name='collaborators', through=Collaborator)

    class Meta:
        db_table = 'notes'

    def __str__(self) -> str:
        return f'{self.title}'
    
class Label(models.Model):
    name = models.CharField(max_length = 255, null = True)
    user = models.ForeignKey(User, on_delete = models.CASCADE)

    class Meta:
        db_table = 'label'

    def __str__(self) -> str:
        return f'{self.name}'
    
@receiver(post_save, sender=Notes)
def set_reminder(instance, **kwargs):
    reminder = instance.reminder
    if reminder:
        # Calculate the reminder time based on the reminder datetime and the current time
        reminder_time = timezone.make_aware(datetime(reminder.year, reminder.month, reminder.day, reminder.hour, reminder.minute))
        
        # Calculate the time difference between the current time and the reminder time
        time_difference = reminder_time - timezone.now()

        # If the reminder time is in the future, schedule the reminder
        if time_difference.total_seconds() > 0:
            # Calculate the time 5 hours and 30 minutes before the reminder time
            delta = timedelta(hours=5, minutes=30)
            reminder_time = reminder_time - delta
            
            crontab, _ = CrontabSchedule.objects.get_or_create(minute=reminder_time.minute,
                hour=reminder_time.hour,
                day_of_month=reminder_time.day,
                month_of_year=reminder_time.month
            )
            
            task = PeriodicTask.objects.filter(name=f"note-{instance.id}--user-{instance.user.id}").first()
            if task:
                task.crontab = crontab
                task.save()
            else:
                task = PeriodicTask.objects.create(
                    crontab=crontab,
                    name=f"note-{instance.id}--user-{instance.user.id}",
                    task='user.tasks.celery_send_mail',
                    args=json.dumps([f'{instance.title}', 'Reminder for notes', settings.EMAIL_HOST_USER, [instance.user.email]])
                )
                
@receiver(post_save, sender=Notes)
def update_or_create_reminder(instance, **kwargs):
    reminder = instance.reminder
    if reminder:
        # Calculate the reminder time based on the reminder datetime and the current time
        reminder_time = timezone.make_aware(datetime(reminder.year, reminder.month, reminder.day, reminder.hour, reminder.minute))
        
        # Calculate the time difference between the current time and the reminder time
        time_difference = reminder_time - timezone.now()

        # If the reminder time is in the future, schedule the reminder
        if time_difference.total_seconds() > 0:
            # Calculate the time 5 hours and 30 minutes before the reminder time
            delta = timedelta(hours=5, minutes=30)
            reminder_time = reminder_time - delta
            
            crontab, _ = CrontabSchedule.objects.get_or_create(minute=reminder_time.minute,
                hour=reminder_time.hour,
                day_of_month=reminder_time.day,
                month_of_year=reminder_time.month
            )
            
            task = PeriodicTask.objects.filter(name=f"note-{instance.id}--user-{instance.user.id}").first()
            if task:
                task.crontab = crontab
                task.args = json.dumps([f'{instance.title}', 'Reminder for notes', settings.EMAIL_HOST_USER, [instance.user.email]])
                task.save()
            else:
                task = PeriodicTask.objects.create(
                    crontab=crontab,
                    name=f"note-{instance.id}--user-{instance.user.id}",
                    task='user.tasks.celery_send_mail',
                    args=json.dumps([f'{instance.title}', 'Reminder for notes', settings.EMAIL_HOST_USER, [instance.user.email]])
                )