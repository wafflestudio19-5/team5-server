from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import BoardViewSet, SubBoardView

router = SimpleRouter()
router.register(r'', BoardViewSet, basename='board')

urlpatterns = [
    path('<int:pk>/subboard/', SubBoardView.as_view(), name='get_sub_boards'),
    path('', include(router.urls)),
]