from django.urls import path
from report import views


urlpatterns = [
    path('post/', views.PostReportView.as_view(), name='post_report'),
    path('comment/', views.CommentReportView.as_view(), name='comment_report'),
    path('evaluation/', views.EvaluationReportView.as_view(), name='evaluation_report'),
    path('examinfo/', views.ExamInfoReportView.as_view(), name='examinfo_report'),
    path('chat/', views.ChatReportView.as_view(), name='chat_report'),
]