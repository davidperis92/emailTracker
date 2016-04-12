from django.db import models
from django.contrib.postgres.fields import ArrayField


# class EmailUser(models.Model):
#     address = models.EmailField()

#     def __str__(self):
#         return self.address


class Email(models.Model):
    task_id = models.IntegerField(blank=True, null=True)
    project_name = models.CharField(max_length=200, blank=True, null=True)
    user_story_id = models.IntegerField(blank=True, null=True)

    sender = models.EmailField()
    receivers = ArrayField(models.EmailField())
    copy_receivers = ArrayField(models.EmailField())
    subject = models.CharField(max_length=100)
    text_html = models.TextField()
    text_plain = models.TextField()
    date = models.DateTimeField()

    def __str__(self):
        output = "Task: " + str(self.task_id) + ", "
        output += "Subject: " + self.subject
        return output


# class TaigaUser(models.Model):
#     user_id = models.IntegerField(primary_key=True)
#     username = models.TextField()
#     token = models.TextField()
#     email = models.EmailField()

#     def __str__(self):
#         return self.username
