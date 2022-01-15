from django.urls import path

from lecture import views

urlpatterns = [
    path('recent/', views.RecentEvalView.as_view(), name='recent_evaluation_list'), # 스크롤 유념
    # path('mine/', views.MyCourseView.as_view(), name='my_course_list'),
    path('<int:pk>/', views.CourseInfoForEvalView.as_view(), name='course_info'),
    # path('<int:pk>/summary/', views.EvalSummaryView.as_view(), name='evaluation_summary'),
    path('<int:pk>/eval/', views.EvaluationView.as_view(), name='get_or_create_evaluation'),
    # path('<int:pk>/examinfo/', views.ExamInfoView.as_view(), name='get_or_create_exam_info'),

    # path('search/', views.CourseSearchView.as_view(), name='course_search'),
    # path('<int:pk>/eval/<int:eval_pk>/like/', views.LikeEvaluationView.as_view(), name='like_evaluation'),
    # path('<int:pk>/examinfo/<int:exam_pk>/like/', views.LikeExamInfoView.as_view(), name='like_exam_info'),
    # path('<int:pk>/point/', views.UsePointView.as_view(), name='use_point'),
]