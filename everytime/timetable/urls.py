from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import TimeTableViewSet

router = SimpleRouter()
router.register(r'', TimeTableViewSet, basename='timetable')

urlpatterns = [
    path('', include(router.urls)) # this url should be last order (because it contains all of urls)
]
