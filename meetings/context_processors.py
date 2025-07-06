# meetings/context_processors.py - معالج سياق لإعدادات الموقع
from .models import SiteSettings

def site_settings(request):
    """إضافة إعدادات الموقع إلى سياق القوالب"""
    return {
        'site_settings': SiteSettings.get_settings(),
    }