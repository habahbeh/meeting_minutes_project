# ===========================================
# meetings/views.py
# ===========================================

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.views.generic import ListView, DetailView
from django.http import JsonResponse, HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.http import require_POST
import json

from .models import (
    Meeting, MeetingTask, MeetingDecision,
    MeetingComment, MeetingApproval, MeetingParticipant
)
from .forms import (
    MeetingUploadForm, MeetingEditForm, MeetingCommentForm,
    MeetingTaskForm, MeetingDecisionForm, MeetingApprovalForm,
    MeetingParticipantForm
)
from .services import MeetingProcessor, MeetingExporter


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        meeting = self.get_object()

        # إضافة نماذج التعليقات والموافقات
        context['comment_form'] = MeetingCommentForm()
        context['approval_form'] = MeetingApprovalForm()

        # الحصول على التعليقات
        context['comments'] = meeting.comments.all().select_related('user')

        # الحصول على المهام والقرارات
        context['tasks'] = meeting.tasks.all()
        context['decisions'] = meeting.decisions.all()

        # الحصول على الموافقات
        context['approvals'] = meeting.approvals.all().select_related('user')

        # الحصول على المشاركين
        context['participants'] = meeting.participants.all()

        return context


def upload_meeting(request):
    """رفع ومعالجة اجتماع جديد"""
    if request.method == 'POST':
        form = MeetingUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # حفظ الاجتماع
                meeting = form.save(commit=False)
                if request.user.is_authenticated:
                    meeting.created_by = request.user
                meeting.save()

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


# @login_required
def edit_meeting(request, pk):
    """تحرير محضر الاجتماع"""
    meeting = get_object_or_404(Meeting, pk=pk)

    # التحقق من الصلاحيات
    if meeting.created_by and meeting.created_by != request.user and not request.user.is_staff:
        messages.error(request, 'ليس لديك صلاحية تحرير هذا المحضر.')
        return redirect('meeting_detail', pk=meeting.pk)

    if request.method == 'POST':
        form = MeetingEditForm(request.POST, instance=meeting)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم حفظ التغييرات بنجاح.')
            return redirect('meeting_detail', pk=meeting.pk)
    else:
        form = MeetingEditForm(instance=meeting)

    return render(request, 'meetings/edit_meeting.html', {
        'form': form,
        'meeting': meeting
    })


# @login_required
def meeting_tasks(request, pk):
    """إدارة مهام الاجتماع"""
    meeting = get_object_or_404(Meeting, pk=pk)

    if request.method == 'POST':
        form = MeetingTaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.meeting = meeting
            task.save()
            messages.success(request, 'تمت إضافة المهمة بنجاح.')
            return redirect('meeting_tasks', pk=meeting.pk)
    else:
        form = MeetingTaskForm()

    tasks = meeting.tasks.all()

    return render(request, 'meetings/tasks.html', {
        'meeting': meeting,
        'tasks': tasks,
        'form': form
    })


# @login_required
def meeting_decisions(request, pk):
    """إدارة قرارات الاجتماع"""
    meeting = get_object_or_404(Meeting, pk=pk)

    if request.method == 'POST':
        form = MeetingDecisionForm(request.POST)
        if form.is_valid():
            decision = form.save(commit=False)
            decision.meeting = meeting
            decision.save()
            messages.success(request, 'تم إضافة القرار بنجاح.')
            return redirect('meeting_decisions', pk=meeting.pk)
    else:
        form = MeetingDecisionForm()

    decisions = meeting.decisions.all()

    return render(request, 'meetings/decisions.html', {
        'meeting': meeting,
        'decisions': decisions,
        'form': form
    })


# @login_required
def add_comment(request, pk):
    """إضافة تعليق على الاجتماع"""
    meeting = get_object_or_404(Meeting, pk=pk)

    if request.method == 'POST':
        form = MeetingCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.meeting = meeting
            comment.user = request.user
            comment.save()

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'comment_id': comment.id,
                    'user_name': comment.user.get_full_name() or comment.user.username,
                    'content': comment.content,
                    'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M')
                })

            messages.success(request, 'تم إضافة التعليق بنجاح.')
            return redirect('meeting_detail', pk=meeting.pk)

    return redirect('meeting_detail', pk=meeting.pk)


# @login_required
def delete_comment(request, comment_id):
    """حذف تعليق"""
    comment = get_object_or_404(MeetingComment, pk=comment_id)

    # التحقق من الصلاحيات
    if comment.user != request.user and not request.user.is_staff:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': 'ليس لديك صلاحية حذف هذا التعليق.'}, status=403)

        messages.error(request, 'ليس لديك صلاحية حذف هذا التعليق.')
        return redirect('meeting_detail', pk=comment.meeting.pk)

    meeting_pk = comment.meeting.pk
    comment.delete()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})

    messages.success(request, 'تم حذف التعليق بنجاح.')
    return redirect('meeting_detail', pk=meeting_pk)


# @login_required
def meeting_approvals(request, pk):
    """عرض حالة الموافقات على المحضر"""
    meeting = get_object_or_404(Meeting, pk=pk)
    approvals = meeting.approvals.all().select_related('user')

    return render(request, 'meetings/approvals.html', {
        'meeting': meeting,
        'approvals': approvals
    })


# @login_required
def approve_meeting(request, pk):
    """الموافقة على محضر الاجتماع"""
    meeting = get_object_or_404(Meeting, pk=pk)

    # التحقق من وجود موافقة سابقة
    approval, created = MeetingApproval.objects.get_or_create(
        meeting=meeting,
        user=request.user,
        defaults={'status': 'pending'}
    )

    if request.method == 'POST':
        form = MeetingApprovalForm(request.POST, instance=approval)
        if form.is_valid():
            form.save()

            # تحديث حالة المحضر إذا كان عدد الموافقات كافياً
            approved_count = meeting.approvals.filter(status='approved').count()
            if approved_count >= 2 and meeting.status == 'pending':
                meeting.status = 'approved'
                meeting.save()

            messages.success(request, 'تم تسجيل موافقتك بنجاح.')
            return redirect('meeting_detail', pk=meeting.pk)
    else:
        form = MeetingApprovalForm(instance=approval)

    return render(request, 'meetings/approve.html', {
        'meeting': meeting,
        'form': form,
        'approval': approval
    })


# @login_required
def meeting_participants(request, pk):
    """إدارة المشاركين في الاجتماع"""
    meeting = get_object_or_404(Meeting, pk=pk)

    if request.method == 'POST':
        form = MeetingParticipantForm(request.POST)
        if form.is_valid():
            participant = form.save(commit=False)
            participant.meeting = meeting
            participant.save()
            messages.success(request, 'تمت إضافة المشارك بنجاح.')
            return redirect('meeting_participants', pk=meeting.pk)
    else:
        form = MeetingParticipantForm()

    participants = meeting.participants.all()

    return render(request, 'meetings/participants.html', {
        'meeting': meeting,
        'participants': participants,
        'form': form
    })


def export_meeting(request, pk, format):
    """تصدير محضر الاجتماع بصيغ مختلفة"""
    meeting = get_object_or_404(Meeting, pk=pk)

    try:
        exporter = MeetingExporter()

        if format == 'pdf':
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{meeting.title}.pdf"'
            response.write(exporter.export_to_pdf(meeting))
            return response

        elif format == 'docx':
            response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            response['Content-Disposition'] = f'attachment; filename="{meeting.title}.docx"'
            response.write(exporter.export_to_docx(meeting))
            return response

        elif format == 'txt':
            response = HttpResponse(content_type='text/plain; charset=utf-8')
            response['Content-Disposition'] = f'attachment; filename="{meeting.title}.txt"'
            response.write(exporter.export_to_txt(meeting))
            return response

        else:
            raise Http404("صيغة التصدير غير مدعومة")

    except Exception as e:
        messages.error(request, f'حدث خطأ أثناء تصدير المحضر: {str(e)}')
        return redirect('meeting_detail', pk=meeting.pk)


# ========== طرق العرض API ==========

@require_POST
# @login_required
def add_task_api(request):
    """إضافة مهمة جديدة (API)"""
    try:
        data = json.loads(request.body)
        meeting_id = data.get('meeting_id')
        meeting = get_object_or_404(Meeting, pk=meeting_id)

        task = MeetingTask.objects.create(
            meeting=meeting,
            description=data.get('description', ''),
            assigned_to=data.get('assigned_to', ''),
            due_date=data.get('due_date')
        )

        return JsonResponse({
            'status': 'success',
            'task_id': task.id
        })

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)


@require_POST
# @login_required
def update_task_api(request, task_id):
    """تحديث مهمة (API)"""
    try:
        task = get_object_or_404(MeetingTask, pk=task_id)
        data = json.loads(request.body)

        task.description = data.get('description', task.description)
        task.assigned_to = data.get('assigned_to', task.assigned_to)
        task.due_date = data.get('due_date', task.due_date)
        task.status = data.get('status', task.status)
        task.save()

        return JsonResponse({
            'status': 'success'
        })

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)


@require_POST
# @login_required
def delete_task_api(request, task_id):
    """حذف مهمة (API)"""
    try:
        task = get_object_or_404(MeetingTask, pk=task_id)
        task.delete()

        return JsonResponse({
            'status': 'success'
        })

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)


@require_POST
# @login_required
def add_decision_api(request):
    """إضافة قرار جديد (API)"""
    try:
        data = json.loads(request.body)
        meeting_id = data.get('meeting_id')
        meeting = get_object_or_404(Meeting, pk=meeting_id)

        decision = MeetingDecision.objects.create(
            meeting=meeting,
            description=data.get('description', ''),
            decision_number=data.get('decision_number', '')
        )

        return JsonResponse({
            'status': 'success',
            'decision_id': decision.id
        })

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)


@require_POST
# @login_required
def update_decision_api(request, decision_id):
    """تحديث قرار (API)"""
    try:
        decision = get_object_or_404(MeetingDecision, pk=decision_id)
        data = json.loads(request.body)

        decision.description = data.get('description', decision.description)
        decision.decision_number = data.get('decision_number', decision.decision_number)
        decision.save()

        return JsonResponse({
            'status': 'success'
        })

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)


@require_POST
# @login_required
def delete_decision_api(request, decision_id):
    """حذف قرار (API)"""
    try:
        decision = get_object_or_404(MeetingDecision, pk=decision_id)
        decision.delete()

        return JsonResponse({
            'status': 'success'
        })

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)