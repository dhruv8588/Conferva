from django.contrib import admin

from .models import Author, Keywords, Paper, Paper_Reviewer, Review, Reviewer

# Register your models here.
class KeywordsAdmin(admin.ModelAdmin):
    list_display = ['name', 'paper']

class KeywordsInline(admin.TabularInline):
    model = Keywords

class ReviewerInline(admin.TabularInline):
    model = Paper.reviewers.through

class PaperAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'submitter', 'conference', 'written_by', 'reviewed_by', 'keywords']
    inlines = [ReviewerInline, KeywordsInline]

    def keywords(self, obj):
        return ", ".join([k.name for k in obj.keywords.all()])
    
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'user', 'email']

class ReviewerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'user', 'email']

class ReviewAdmin(admin.ModelAdmin):
    list_display = ['paper', 'reviewer', 'body', 'date_reviewed']   

class Paper_ReviewerAdmin(admin.ModelAdmin):
    list_display = ['paper', 'reviewer', 'status']


admin.site.register(Paper, PaperAdmin)
admin.site.register(Author, AuthorAdmin)
admin.site.register(Reviewer, ReviewerAdmin)
admin.site.register(Paper_Reviewer, Paper_ReviewerAdmin)
admin.site.register(Keywords, KeywordsAdmin)
admin.site.register(Review, ReviewAdmin)
