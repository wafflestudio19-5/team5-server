from django.db import models


class Comment(models.Model):
    # 연결된 게시글, 게시글이 삭제되면 댓글도 삭제됨
    post = models.ForeignKey('post.Post', on_delete=models.CASCADE, null=True)
    # 작성자가 탈퇴해도 글은 남아있으므로 set_null, 작성자가 없으면 (알수없음)으로 뜸
    writer = models.ForeignKey('user.User', on_delete=models.SET_NULL, null=True)

    content = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    num_of_likes = models.PositiveIntegerField(default=0, blank=True)
    is_anonymous = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    # 대댓글 기능
    # 하나의 댓글 당 하나의 윗 댓글을 가질 수 있음. 아래의 예시에서 B, C 모두 A에 종속되는 댓글임. A 는 윗 댓글이 없고 B, C는 윗댓글이 A임.
    # ex. A (댓글)
    #     ㄴ B (대댓글)
    #     ㄴ C (대댓글)
    # 윗댓글을 head_comment라 하고, ForeignKey 재귀참조를 사용해봄.
    # 어떤 댓글은 A처럼 윗댓글이 없을 수 있으므로 head_comment의 null 허용. 즉 head_comment가 null이면 댓글이고 null이 아니면 대댓글임.
    # 댓글이 삭제되어도 그에 종속되는 대댓글은 사라지지 않으므로 on_delete 는 do_nothing (사실 삭제하면 on_delete를 true로 만드니 댓글레코드 삭제는 없을듯)
    # on_delete를 set_null로 할 수는 없음 - 댓글과 대댓글을 구분해야하기 때문
    head_comment = models.ForeignKey('self', related_name='tail_comments', on_delete=models.DO_NOTHING, null=True)

    def __str__(self):
        return self.content

