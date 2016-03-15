import datetime
from django.db import models
from django.utils import timezone


class EmailUser(models.Model):
    email = models.EmailField()
    def __str__(self):
        return self.email


class Email(models.Model):
    task_id = models.IntegerField()
    project_id = models.IntegerField()
    user_story_id = models.IntegerField()

    sender = models.ForeignKey(EmailUser, related_name='emailUser_sender')
    receiver = models.ManyToManyField(EmailUser, related_name='emailUser_receiver')
    copy_receiver = models.ManyToManyField(EmailUser, related_name='emailUser_copy')
    subject = models.CharField(max_length=500)
    text = models.TextField()
    date = models.DateTimeField()

    def __str__(self):
        output = "Task: " + str(self.task_id) + ", "
        output += "Subject: " + self.subject
        return output

class TaigaManager(models.Manager):
    def create_User(self, user_id, username, token, email):
        tUser = self.create(user_id=user_id, username=username, token=token, email=email)
        return tUser

class TaigaUser(models.Model):
    user_id = models.IntegerField(primary_key=True)
    username = models.TextField()
    token = models.TextField()
    email = models.EmailField()

    objects = TaigaManager()
    def __str__(self):
        return self.username
