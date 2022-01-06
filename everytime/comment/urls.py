from django.urls import path

from comment.views import LikeCommentView

urlpatterns = [
    path('<int:pk>/like/', LikeCommentView.as_view(), name='like_comment'),
]