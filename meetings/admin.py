# ===========================================
# meetings/admin.py
# ===========================================

from django.contrib import admin
from .models import (
    Meeting, MeetingTask, MeetingDecision,
    MeetingComment, MeetingApproval, MeetingParticipant
)


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    """إدارة الاجتماعات في لوحة الإدارة"""

    list_display = ['title', 'is_processed', 'status', 'created_by', 'created_at']
    list_filter = ['status', 'created_at', 'is_public']
    search_fields = ['title']
    readonly_fields = ['transcript', 'summary', 'minutes', 'created_at', 'updated_at']

    fieldsets = (
        ('المعلومات الأساسية', {
            'fields': ('title', 'audio_file', 'created_by', 'is_public', 'status')
        }),
        ('النتائج', {
            'fields': ('transcript', 'summary', 'minutes'),
            'classes': ('collapse',)
        }),
        ('التواريخ', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(MeetingTask)
class MeetingTaskAdmin(admin.ModelAdmin):
    """إدارة المهام في لوحة الإدارة"""

    list_display = ['description', 'meeting', 'assigned_to', 'due_date', 'status', 'created_at']
    list_filter = ['status', 'due_date', 'created_at']
    search_fields = ['description', 'assigned_to']
    raw_id_fields = ['meeting']


@admin.register(MeetingDecision)
class MeetingDecisionAdmin(admin.ModelAdmin):
    """إدارة القرارات في لوحة الإدارة"""

    list_display = ['description', 'meeting', 'decision_number', 'created_at']
    search_fields = ['description', 'decision_number']
    raw_id_fields = ['meeting']


@admin.register(MeetingComment)
class MeetingCommentAdmin(admin.ModelAdmin):
    """إدارة التعليقات في لوحة الإدارة"""

    list_display = ['content', 'meeting', 'user', 'section', 'created_at']
    list_filter = ['section', 'created_at']
    search_fields = ['content']
    raw_id_fields = ['meeting', 'user']


@admin.register(MeetingApproval)
class MeetingApprovalAdmin(admin.ModelAdmin):
    """إدارة الموافقات في لوحة الإدارة"""

    list_display = ['meeting', 'user', 'status', 'created_at', 'updated_at']
    list_filter = ['status', 'created_at', 'updated_at']
    search_fields = ['comments']
    raw_id_fields = ['meeting', 'user']


@admin.register(MeetingParticipant)
class MeetingParticipantAdmin(admin.ModelAdmin):
    """إدارة المشاركين في لوحة الإدارة"""

    list_display = ['name', 'meeting', 'email', 'role', 'created_at']
    search_fields = ['name', 'email', 'role']
    raw_id_fields = ['meeting', 'user']