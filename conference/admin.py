from django.contrib import admin

from .models import Author, Conference, Paper

class PaperAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'submitter', 'conference', 'written_by']

class ConferenceAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'creator', 'is_approved', 'submission_deadline']
    list_editable = ('is_approved',)

class AuthorAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'user', 'email']

# Register your models here.
admin.site.register(Conference, ConferenceAdmin)
admin.site.register(Paper, PaperAdmin)
admin.site.register(Author, AuthorAdmin)