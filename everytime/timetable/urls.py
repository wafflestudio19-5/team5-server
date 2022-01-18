from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import TimeTableView

router = SimpleRouter()
router.register(r'', TimeTableView, basename='timetable')

urlpatterns = [
    path('', include(router.urls)) # this url should be last order (because it contains all of urls)
]
