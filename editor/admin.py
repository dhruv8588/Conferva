from django.contrib import admin

from .models import Editor

class EditorAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_approved', 'created_at')
    list_display_links = ('user',)
    list_editable = ('is_approved',)

# Register your models here.
admin.site.register(Editor, EditorAdmin)