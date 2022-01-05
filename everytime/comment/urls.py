from django.urls import path

from comment.views import LikeCommentView

urlpatterns = [
    path('like/<int:pk>/', LikeCommentView.as_view(), name='like_comment'),
]