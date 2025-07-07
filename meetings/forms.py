# ===========================================
# meetings/forms.py
# ===========================================

from django import forms
from .models import Meeting, MeetingComment, MeetingTask, MeetingDecision, MeetingApproval, MeetingParticipant


class MeetingUploadForm(forms.ModelForm):
    """نموذج رفع الاجتماع"""

    class Meta:
        model = Meeting
        fields = ['title', 'audio_file', 'is_public']
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
            }),
            'is_public': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
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


class MeetingEditForm(forms.ModelForm):
    """نموذج تحرير محضر الاجتماع"""

    class Meta:
        model = Meeting
        fields = ['title', 'minutes', 'summary']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'required': True
            }),
            'minutes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 15,
                'dir': 'rtl'
            }),
            'summary': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 8,
                'dir': 'rtl'
            })
        }


class MeetingCommentForm(forms.ModelForm):
    """نموذج إضافة تعليق"""

    class Meta:
        model = MeetingComment
        fields = ['content', 'section', 'reference_id']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'أضف تعليقك هنا...',
                'required': True
            }),
            'section': forms.HiddenInput(),
            'reference_id': forms.HiddenInput()
        }


class MeetingTaskForm(forms.ModelForm):
    """نموذج إضافة مهمة"""

    class Meta:
        model = MeetingTask
        fields = ['description', 'assigned_to', 'due_date', 'status']
        widgets = {
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'وصف المهمة',
                'required': True
            }),
            'assigned_to': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'الشخص المسؤول'
            }),
            'due_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            })
        }


class MeetingDecisionForm(forms.ModelForm):
    """نموذج إضافة قرار"""

    class Meta:
        model = MeetingDecision
        fields = ['description', 'decision_number']
        widgets = {
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'نص القرار',
                'required': True
            }),
            'decision_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'رقم القرار (اختياري)'
            })
        }


class MeetingApprovalForm(forms.ModelForm):
    """نموذج الموافقة على المحضر"""

    class Meta:
        model = MeetingApproval
        fields = ['status', 'comments']
        widgets = {
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'comments': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'ملاحظات (اختيارية)'
            })
        }


class MeetingParticipantForm(forms.ModelForm):
    """نموذج إضافة مشارك"""

    class Meta:
        model = MeetingParticipant
        fields = ['name', 'email', 'role']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'اسم المشارك',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'البريد الإلكتروني'
            }),
            'role': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'الدور في الاجتماع'
            })
        }