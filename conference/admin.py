from django.contrib import admin

from .models import Author, Conference, Keywords, Paper, Paper_Reviewer, Reviewer

class ReviewerInline(admin.TabularInline):
    model = Paper.reviewers.through

class KeywordsInline(admin.TabularInline):
    model = Keywords

class PaperAdmin(admin.ModelAdmin):
    list_display = ['title', 'submitter', 'conference', 'written_by', 'reviewed_by', 'keywords']
    inlines = [ReviewerInline, KeywordsInline]

    def keywords(self, obj):
        return ", ".join([k.name for k in obj.keywords.all()])


class ReviewerAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'user', 'email']

class ConferenceAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'creator', 'is_approved', 'submission_deadline']
    list_editable = ('is_approved',)

class AuthorAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'user', 'email']

class KeywordsAdmin(admin.ModelAdmin):
    list_display = ['name', 'paper']


# Register your models here.
admin.site.register(Conference, ConferenceAdmin)
admin.site.register(Paper, PaperAdmin)
admin.site.register(Author, AuthorAdmin)
admin.site.register(Reviewer, ReviewerAdmin)

admin.site.register(Paper_Reviewer)
admin.site.register(Keywords, KeywordsAdmin)