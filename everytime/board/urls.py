from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import BoardView


urlpatterns = [
    path('', BoardView.as_view(), name='create_or_get_board'),
]