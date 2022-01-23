from django.urls import path
from .views import *

urlpatterns = [
    path('', MessageThroughPostOrCommentView.as_view()),
    path('<int:pk>/', MessageThroughChatRoomView.as_view()),
    path('list/', ChatRoomListView.as_view())
]