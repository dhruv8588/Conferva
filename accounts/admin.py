from django.contrib import admin
from .models import ResearchArea, User, UserProfile
from django.contrib.auth.admin import UserAdmin

# Register your models here.

class ResearchAreaInline(admin.TabularInline):
    model = ResearchArea

class CustomUserAdmin(UserAdmin):
    inlines = [
        ResearchAreaInline,
    ]
    list_display = ('id', 'email', 'first_name', 'last_name', 'username', 'is_admin', 'is_active', 'research_areas')
    ordering = ('-date_joined',)
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

    def research_areas(self, obj):
        return ", ".join([k.name for k in obj.research_areas.all()])

class ResearchAreaAdmin(admin.ModelAdmin):
    list_display = ['name', 'user']

admin.site.register(User, CustomUserAdmin)
admin.site.register(UserProfile)
admin.site.register(ResearchArea, ResearchAreaAdmin)

