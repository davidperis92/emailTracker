from django.contrib import admin
from .models import Email, EmailUser


class EmailUserAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Email',   {'fields': ['email']}),
    ]
    list_filter = ['email']
    search_fields = ['email']

class EmailAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Taiga Task',          {'fields': ['task_id']}),
        ('Taiga Project',       {'fields': ['project_id']}),
        ('User Story',          {'fields': ['user_story_id']}),
        ('From',                {'fields': ['sender']}),
        ('To',                  {'fields': ['receiver']}),
        ('CC',                {'fields': ['copy_receiver']}),
        ('Subject',             {'fields': ['subject']}),
        ('Text',                {'fields': ['text']}),
        ('Date',                {'fields': ['date']}),
    ]
    list_display = ('task_id', 'project_id', 'user_story_id', 'sender', 'subject', 'text', 'date')
    list_filter = ['sender']
    search_fields = ['task_id', 'sender', 'receiver', 'subject']

admin.site.register(Email, EmailAdmin)
admin.site.register(EmailUser, EmailUserAdmin)
