# ===========================================
# meetings/forms.py
# ===========================================

from django import forms
from .models import Meeting


class MeetingUploadForm(forms.ModelForm):
    """نموذج رفع الاجتماع"""

    class Meta:
        model = Meeting
        fields = ['title', 'audio_file']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'أدخل عنوان الاجتماع',
                'required': True
            }),
            'audio_file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'audio/*',
                'required': True
            })
        }

    def clean_audio_file(self):
        """التحقق من صحة الملف الصوتي"""
        audio_file = self.cleaned_data.get('audio_file')

        if audio_file:
            # التحقق من حجم الملف (25 ميجابايت)
            if audio_file.size > 25 * 1024 * 1024:
                raise forms.ValidationError('حجم الملف كبير جداً. الحد الأقصى 25 ميجابايت.')

            # التحقق من نوع الملف
            allowed_types = ['audio/mpeg', 'audio/wav', 'audio/mp4', 'audio/ogg']
            if audio_file.content_type not in allowed_types:
                raise forms.ValidationError('نوع الملف غير مدعوم. استخدم MP3, WAV, M4A أو OGG.')

        return audio_file