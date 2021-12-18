from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import BoardCreateView


urlpatterns = [
    path('', BoardCreateView.as_view(), name='create_board'),
]