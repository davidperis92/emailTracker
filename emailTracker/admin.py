from django.contrib import admin
from .models import Email, LogTask, LogUserStory, Task, UserStory, Project, TaigaUser


# class EmailUserAdmin(admin.ModelAdmin):
#     fieldsets = [
#         ('Address',   {'fields': ['address']}),
#     ]
#     list_filter = ['address']
#     search_fields = ['address']


# class EmailAdmin(admin.ModelAdmin):
#     fieldsets = [
#         ('Taiga Task',          {'fields': ['task_id']}),
#         ('Taiga Project',       {'fields': ['project_id']}),
#         ('User Story',          {'fields': ['user_story_id']}),
#         ('From',                {'fields': ['sender']}),
#         ('To',                  {'fields': ['receiver']}),
#         ('CC',                  {'fields': ['copy_receiver']}),
#         ('Subject',             {'fields': ['subject']}),
#         ('HTML Text',           {'fields': ['text_html']}),
#         ('Plain Text',          {'fields': ['text_plain']}),
#         ('Date',                {'fields': ['date']}),
#     ]
#     list_display = ('task_id', 'project_id', 'user_story_id', 'sender', 'subject', 'text', 'date')
#     list_filter = ['sender']
#     search_fields = ['task_id', 'sender', 'receiver', 'subject']


# admin.site.register(Email, EmailAdmin)
# admin.site.register(EmailUser, EmailUserAdmin)
admin.site.register(Email)
admin.site.register(LogTask)
admin.site.register(LogUserStory)
admin.site.register(Task)
admin.site.register(UserStory)
admin.site.register(Project)
admin.site.register(TaigaUser)
