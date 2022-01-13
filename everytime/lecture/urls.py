from django.urls import path

from lecture.views import CourseForEvalView

urlpatterns = [
    path('<int:pk>/', CourseForEvalView.as_view(), name='course_info'),
]