from django.db import models
from django.urls import reverse


class Meeting(models.Model):
    """نموذج الاجتماع"""

    title = models.CharField(max_length=200, verbose_name="عنوان الاجتماع")
    audio_file = models.FileField(upload_to='audio/', verbose_name="الملف الصوتي")
    transcript = models.TextField(blank=True, null=True, verbose_name="النص المحول")
    summary = models.TextField(blank=True, null=True, verbose_name="التلخيص")
    minutes = models.TextField(blank=True, null=True, verbose_name="محضر الاجتماع")

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