# ===========================================
# meetings/admin.py
# ===========================================

from django.contrib import admin
from .models import Meeting


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    """إدارة الاجتماعات في لوحة الإدارة"""

    list_display = ['title', 'is_processed', 'created_at']
    list_filter = ['created_at']
    search_fields = ['title']
    readonly_fields = ['transcript', 'summary', 'minutes', 'created_at', 'updated_at']

    fieldsets = (
        ('المعلومات الأساسية', {
            'fields': ('title', 'audio_file')
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