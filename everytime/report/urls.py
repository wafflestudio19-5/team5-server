from django.urls import path
from report import views


urlpatterns = [
    path('post/', views.PostReportView.as_view(), name='post_report'),
]