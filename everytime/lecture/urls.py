from django.urls import path

from lecture.views import CourseForEvalView, LectureSearchViewSet

urlpatterns = [
    path('<int:pk>/', CourseForEvalView.as_view(), name='course_info'),
    path('search/', LectureSearchViewSet.as_view({'get':'list'}), name='lecture_search'),
]