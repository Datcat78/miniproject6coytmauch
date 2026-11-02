### INF601 - Advanced Programming in Python
### Coyt Mauch
### Mini Project 6

from django.contrib import admin, messages
from django.utils import timezone

from .models import Assignment

admin.site.site_header = 'Student Assignment Tracker Admin'
admin.site.site_title = 'Assignment Tracker Admin'
admin.site.index_title = 'Manage users and assignments'


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'course_name', 'owner', 'due_date', 'priority', 'is_completed', 'overdue')
    list_filter = ('is_completed', 'priority', 'due_date', 'course_name', 'owner')
    search_fields = ('title', 'course_name', 'description', 'owner__username')
    date_hierarchy = 'due_date'
    list_select_related = ('owner',)
    list_per_page = 25
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {'fields': ('owner', 'title', 'course_name', 'description')}),
        ('Status', {'fields': ('due_date', 'priority', 'is_completed')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    actions = ('mark_completed', 'mark_incomplete')

    @admin.display(boolean=True, description='Overdue')
    def overdue(self, obj):
        return obj.is_overdue

    @admin.action(description='Mark selected assignments as completed')
    def mark_completed(self, request, queryset):
        # update() skips auto_now, so set updated_at explicitly.
        count = queryset.update(is_completed=True, updated_at=timezone.now())
        self.message_user(request, f'{count} assignment(s) marked as completed.', messages.SUCCESS)

    @admin.action(description='Mark selected assignments as not completed')
    def mark_incomplete(self, request, queryset):
        count = queryset.update(is_completed=False, updated_at=timezone.now())
        self.message_user(request, f'{count} assignment(s) marked as not completed.', messages.SUCCESS)
