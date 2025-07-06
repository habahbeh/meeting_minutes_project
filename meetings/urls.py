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
]