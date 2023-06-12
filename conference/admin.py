from django.contrib import admin

from .models import Author, Conference, Paper

class PaperAdmin(admin.ModelAdmin):
    # list_display = ['title', 'written_by', 'submitted_in']
    list_display = ['title', 'submitted_in']

class ConferenceAdmin(admin.ModelAdmin):
    list_display = ['name', 'id', 'submitted_by', 'is_approved']
    list_editable = ('is_approved',)

# Register your models here.
admin.site.register(Conference, ConferenceAdmin)
admin.site.register(Paper, PaperAdmin)
admin.site.register(Author)