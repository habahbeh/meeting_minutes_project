from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User


class Meeting(models.Model):
    """نموذج الاجتماع"""

    title = models.CharField(max_length=200, verbose_name="عنوان الاجتماع")
    audio_file = models.FileField(upload_to='audio/', verbose_name="الملف الصوتي")
    transcript = models.TextField(blank=True, null=True, verbose_name="النص المحول")
    summary = models.TextField(blank=True, null=True, verbose_name="التلخيص")
    minutes = models.TextField(blank=True, null=True, verbose_name="محضر الاجتماع")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='meetings',
                                   verbose_name="تم إنشاؤه بواسطة", null=True)
    is_public = models.BooleanField(default=False, verbose_name="متاح للجميع")
    status = models.CharField(max_length=20, choices=[
        ('draft', 'مسودة'),
        ('pending', 'قيد الموافقة'),
        ('approved', 'تمت الموافقة')
    ], default='draft', verbose_name="حالة المحضر")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "اجتماع"
        verbose_name_plural = "الاجتماعات"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('meeting_detail', kwargs={'pk': self.pk})

    @property
    def is_processed(self):
        """تحقق من معالجة الاجتماع"""
        return bool(self.transcript and self.summary and self.minutes)


class MeetingTask(models.Model):
    """نموذج المهام المستخرجة من الاجتماع"""

    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name='tasks', verbose_name="الاجتماع")
    description = models.TextField(verbose_name="وصف المهمة")
    assigned_to = models.CharField(max_length=100, blank=True, null=True, verbose_name="مسند إلى")
    due_date = models.DateField(blank=True, null=True, verbose_name="تاريخ الاستحقاق")
    status = models.CharField(max_length=20, choices=[
        ('pending', 'قيد التنفيذ'),
        ('completed', 'مكتملة'),
        ('cancelled', 'ملغاة')
    ], default='pending', verbose_name="الحالة")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "مهمة"
        verbose_name_plural = "المهام"
        ordering = ['due_date', 'created_at']

    def __str__(self):
        return f"مهمة: {self.description[:50]}"


class MeetingDecision(models.Model):
    """نموذج القرارات المستخرجة من الاجتماع"""

    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name='decisions', verbose_name="الاجتماع")
    description = models.TextField(verbose_name="نص القرار")
    decision_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="رقم القرار")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "قرار"
        verbose_name_plural = "القرارات"
        ordering = ['created_at']

    def __str__(self):
        return f"قرار: {self.description[:50]}"


class MeetingComment(models.Model):
    """نموذج التعليقات على المحضر"""

    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name='comments', verbose_name="الاجتماع")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='meeting_comments', verbose_name="المستخدم")
    content = models.TextField(verbose_name="نص التعليق")
    section = models.CharField(max_length=20, choices=[
        ('minutes', 'المحضر'),
        ('summary', 'التلخيص'),
        ('task', 'المهمة'),
        ('decision', 'القرار')
    ], default='minutes', verbose_name="القسم")
    reference_id = models.IntegerField(blank=True, null=True, verbose_name="معرف المرجع")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "تعليق"
        verbose_name_plural = "التعليقات"
        ordering = ['-created_at']

    def __str__(self):
        return f"تعليق: {self.content[:50]}"


class MeetingApproval(models.Model):
    """نموذج الموافقات على المحضر"""

    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name='approvals', verbose_name="الاجتماع")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='meeting_approvals', verbose_name="المستخدم")
    status = models.CharField(max_length=20, choices=[
        ('pending', 'قيد الانتظار'),
        ('approved', 'موافق'),
        ('rejected', 'مرفوض')
    ], default='pending', verbose_name="حالة الموافقة")
    comments = models.TextField(blank=True, null=True, verbose_name="ملاحظات")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "موافقة"
        verbose_name_plural = "الموافقات"
        ordering = ['-updated_at']
        unique_together = ('meeting', 'user')  # كل مستخدم له موافقة واحدة فقط على الاجتماع

    def __str__(self):
        return f"موافقة: {self.user.username} - {self.get_status_display()}"


class MeetingParticipant(models.Model):
    """نموذج المشاركين في الاجتماع"""

    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name='participants', verbose_name="الاجتماع")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='meeting_participations',
                             verbose_name="المستخدم", null=True, blank=True)
    name = models.CharField(max_length=100, verbose_name="الاسم")
    email = models.EmailField(blank=True, null=True, verbose_name="البريد الإلكتروني")
    role = models.CharField(max_length=50, blank=True, null=True, verbose_name="الدور")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "مشارك"
        verbose_name_plural = "المشاركون"
        ordering = ['name']
        unique_together = ('meeting', 'user')  # كل مستخدم يمكنه المشاركة مرة واحدة فقط في الاجتماع

    def __str__(self):
        return f"مشارك: {self.name}"