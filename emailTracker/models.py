from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.utils.translation import ugettext_lazy as _


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


class Log(models.Model):
    date        = models.DateTimeField()
    action      = models.CharField(max_length=200, blank=False, null=False)
    by          = models.ForeignKey("TaigaUser", null=True, blank=True,
                                related_name="logs", verbose_name=_("by"))


class LogTask(Log, models.Model):
    task        = models.ForeignKey("Task", null=True, blank=True,
                                related_name="logs", verbose_name=_("task"))

    @classmethod
    def create_from_json(self, json_data):
        tUser   = TaigaUser.get_or_create_from_json( json_data['by'] )
        task    = Task.get_or_create_from_json( json_data['data'] )

        LogTask.objects.update_or_create(
            date       = json_data['date'],
            action     = json_data['action'],
            by         = tUser,
            task       = task
        )



class LogUserStory(Log, models.Model):
    userstory   = models.ForeignKey("UserStory", null=True, blank=True,
                                related_name="logs", verbose_name=_("userstory"))

    @classmethod
    def create_from_json(self, json_data):
        tUser       = TaigaUser.get_or_create_from_json( json_data['by'] )
        userstory   = UserStory.get_or_create_from_json( json_data['data'] )

        LogUserStory.objects.update_or_create(
            date          = json_data['date'],
            action        = json_data['action'],
            by            = tUser,
            userstory     = userstory
        )



class Project(models.Model):
    name        = models.CharField(max_length=250, null=False, blank=False,
                                    verbose_name=_("name"))

    @classmethod
    def get_or_create_from_json(self, json_data):
        p, created = Project.objects.get_or_create(
                        id          = json_data['id'],
                        name        = json_data['name']
                    )
        return p



class TaigaUser(models.Model):
    username    = models.CharField(max_length=200, blank=True, null=True)

    @classmethod
    def get_or_create_from_json(self, json_data):
        tu, created = TaigaUser.objects.get_or_create(
                        id          = json_data['id'],
                        username    = json_data['username']
                    )
        return tu




class UserStory(models.Model):
    userstory_id        = models.IntegerField(blank=True, null=True)
    assigned_to         = models.CharField(max_length=200, blank=True, null=True)
    created_date        = models.DateTimeField()
    modified_date       = models.DateTimeField(blank=True, null=True)
    finish_date         = models.DateTimeField(blank=True, null=True)
    subject             = models.CharField(max_length=200, blank=True, null=True)
    description         = models.CharField(max_length=200, blank=True, null=True)
    is_blocked          = models.BooleanField()
    is_closed           = models.BooleanField()

    project             = models.ForeignKey("Project", null=False, blank=False,
                                related_name="user_stories", verbose_name=_("project"))
    owner               = models.ForeignKey("TaigaUser", null=True, blank=True,
                                related_name="owned_user_stories", verbose_name=_("owner"),
                                on_delete=models.SET_NULL)

    @classmethod
    def get_or_create_from_json(self, json_data):
        tUser   = TaigaUser.get_or_create_from_json( json_data['owner'] )

        project = Project.get_or_create_from_json( json_data['project'] )
        #import pdb; pdb.set_trace()
        us, created = UserStory.objects.get_or_create(
                        userstory_id    = json_data['id'],
                        assigned_to     = json_data['assigned_to'],
                        created_date    = json_data['created_date'],
                        modified_date   = json_data['modified_date'],
                        finish_date     = json_data['finish_date'],
                        subject         = json_data['subject'],
                        description     = json_data['description'],
                        is_blocked      = json_data['is_blocked'],
                        is_closed       = json_data['is_closed'],
                        project         = project,
                        owner           = tUser
                    )
        return us


class Task(models.Model):
    task_id             = models.IntegerField(blank=True, null=True)
    assigned_to         = models.CharField(max_length=200, blank=True, null=True)
    created_date        = models.DateTimeField()
    modified_date       = models.DateTimeField(blank=True, null=True)
    finished_date       = models.DateTimeField(blank=True, null=True)
    subject             = models.CharField(max_length=200, blank=True, null=True)
    description         = models.CharField(max_length=200, blank=True, null=True)
    is_blocked          = models.BooleanField()

    user_story          = models.ForeignKey("UserStory", db_column='userstory_id', null=True, blank=True,
                                    related_name="tasks", verbose_name=_("user story"))
    project             = models.ForeignKey("Project", null=False, blank=False,
                                    related_name="tasks", verbose_name=_("project"))
    owner               = models.ForeignKey("TaigaUser", null=True, blank=True,
                                    related_name="owned_tasks", verbose_name=_("owner"),
                                    on_delete=models.SET_NULL)

    @classmethod
    def get_or_create_from_json(self, json_data):
        userstory   = UserStory.get_or_create_from_json( json_data['user_story'] )
        tUser       = TaigaUser.get_or_create_from_json( json_data['owner'] )
        project     = Project.get_or_create_from_json( json_data['project'] )
        #import pdb; pdb.set_trace()
        t, created  = Task.objects.get_or_create(
                        task_id         = json_data['id'],
                        assigned_to     = json_data['assigned_to'],
                        created_date    = json_data['created_date'],
                        modified_date   = json_data['modified_date'],
                        finished_date   = json_data['finished_date'],
                        subject         = json_data['subject'],
                        description     = json_data['description'],
                        is_blocked      = json_data['is_blocked'],
                        user_story      = userstory,
                        project         = project,
                        owner           = tUser
                    )
        return t
