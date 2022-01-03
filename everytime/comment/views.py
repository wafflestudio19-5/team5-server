from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone

from rest_framework import permissions
from rest_framework.views import APIView

import datetime

from comment.models import Comment


# '공감'버튼을 누르면 '이 댓글에 공감하십니까?'라는 팝업창이뜨고, '확인' 버튼을 누르면 호출될 API
# 삭제된 댓글은 공감버튼 자체가 없음
# (알수없음)의 댓글은 공감가능
class LikeCommentView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, pk):
        comment = get_object_or_404(Comment, pk=pk)

        if request.user in comment.like_users.all():  # 이미 공감을 누른 사람이라면
            return HttpResponse('이미 공감한 댓글입니다.')  # '이미 공감한 댓글입니다.'를 담은 팝업창이 떠야함
        elif comment.created_at < (timezone.now() - datetime.timedelta(days=365)):  # 기준은 임의로 정했음, 1년
            return HttpResponse('오래된 댓글은 공감할 수 없습니다.')
        else:
            comment.like_users.add(request.user)
            comment.num_of_likes += 1
            comment.save()
            return_address = 'http://waffle-minkyu.shop/post/'+str(comment.post_id)+'/'  # 해당 댓글을 갖고있는 게시물을 가져오는 API
            return redirect(return_address)
