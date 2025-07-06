# ===========================================
# meetings/views.py
# ===========================================

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.views.generic import ListView, DetailView
from django.http import JsonResponse
from .models import Meeting
from .forms import MeetingUploadForm
from .services import MeetingProcessor

class MeetingListView(ListView):
    """عرض قائمة الاجتماعات"""
    model = Meeting
    template_name = 'meetings/meeting_list.html'
    context_object_name = 'meetings'
    paginate_by = 10

class MeetingDetailView(DetailView):
    """عرض تفاصيل الاجتماع"""
    model = Meeting
    template_name = 'meetings/meeting_detail.html'
    context_object_name = 'meeting'

def upload_meeting(request):
    """رفع ومعالجة اجتماع جديد"""
    if request.method == 'POST':
        form = MeetingUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # حفظ الاجتماع
                meeting = form.save()

                # معالجة الملف الصوتي
                processor = MeetingProcessor()
                success, message = processor.process_meeting(meeting)

                if success:
                    messages.success(request, 'تم معالجة الملف بنجاح! يمكنك الآن مراجعة النتائج.')
                    return redirect('meeting_detail', pk=meeting.pk)
                else:
                    messages.error(request, f'حدث خطأ في المعالجة: {message}')

            except Exception as e:
                messages.error(request, f'حدث خطأ غير متوقع: {str(e)}')
    else:
        form = MeetingUploadForm()

    return render(request, 'meetings/upload.html', {'form': form})

def delete_meeting(request, pk):
    """حذف اجتماع"""
    meeting = get_object_or_404(Meeting, pk=pk)

    if request.method == 'POST':
        meeting.delete()
        messages.success(request, 'تم حذف الاجتماع بنجاح.')
        return redirect('meeting_list')

    return render(request, 'meetings/confirm_delete.html', {'meeting': meeting})