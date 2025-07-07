# ===========================================
# meetings/urls.py
# ===========================================

from django.urls import path
from . import views

urlpatterns = [
    path('', views.MeetingListView.as_view(), name='meeting_list'),
    path('upload/', views.upload_meeting, name='upload_meeting'),
    path('<int:pk>/', views.MeetingDetailView.as_view(), name='meeting_detail'),
    path('<int:pk>/delete/', views.delete_meeting, name='delete_meeting'),

    # المسارات الجديدة
    path('<int:pk>/edit/', views.edit_meeting, name='edit_meeting'),
    path('<int:pk>/tasks/', views.meeting_tasks, name='meeting_tasks'),
    path('<int:pk>/decisions/', views.meeting_decisions, name='meeting_decisions'),
    path('<int:pk>/comments/', views.add_comment, name='add_comment'),
    path('comments/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('<int:pk>/approvals/', views.meeting_approvals, name='meeting_approvals'),
    path('<int:pk>/approve/', views.approve_meeting, name='approve_meeting'),
    path('<int:pk>/participants/', views.meeting_participants, name='meeting_participants'),
    path('<int:pk>/export/<str:format>/', views.export_meeting, name='export_meeting'),

    # مسارات API
    path('api/tasks/add/', views.add_task_api, name='add_task_api'),
    path('api/tasks/<int:task_id>/update/', views.update_task_api, name='update_task_api'),
    path('api/tasks/<int:task_id>/delete/', views.delete_task_api, name='delete_task_api'),
    path('api/decisions/add/', views.add_decision_api, name='add_decision_api'),
    path('api/decisions/<int:decision_id>/update/', views.update_decision_api, name='update_decision_api'),
    path('api/decisions/<int:decision_id>/delete/', views.delete_decision_api, name='delete_decision_api'),
]