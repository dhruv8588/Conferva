from django.contrib import admin

from .models import Conference, Editor

class ConferenceAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'creator', 'is_approved', 'submission_deadline', 'organised_by']
    list_editable = ('is_approved',)
 
class EditorAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'user', 'email']

# Register your models here.
admin.site.register(Conference, ConferenceAdmin)
admin.site.register(Editor, EditorAdmin)

