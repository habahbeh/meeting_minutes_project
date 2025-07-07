# ===========================================
# meetings/apps.py
# ===========================================

from django.apps import AppConfig

class MeetingsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'meetings'
    verbose_name = 'محرر محاضر الاجتماعات'