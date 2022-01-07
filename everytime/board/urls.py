from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import BoardView, SubBoardView


urlpatterns = [
    path('', BoardView.as_view(), name='create_or_get_board'),
    path('<int:pk>/subboard/', SubBoardView.as_view(), name='get_sub_boards')
]