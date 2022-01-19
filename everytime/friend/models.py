from django.db import models

# Create your models here.
class Friend(models.Model):
    user = models.ForeignKey('user.User', on_delete=models.CASCADE)
    friend = models.ForeignKey('user.User', on_delete=models.CASCADE)

    # Meta는 모델의 이너클래스로서, 데이터베이스를 구축할 때 필요한 추가적인 설정들을 할 수 있다.
    class Meta:
        # 두 필드를 합쳐서 composite primary key로 사용 가능
        constraints = [
            models.UniqueConstraint(
                fields=["user", "friend"],
                name="friend relation"
            )
        ]
        # 데이터 기본 정렬 순서 1순위 user 2순위 friend
        ordering = ['user', 'friend']

class FriendRequest(models.Model):
    sender = models.ForeignKey('user.User', on_delete=models.CASCADE)
    receiver = models.ForeignKey('user.User', on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["sender", "receiver"],
                name="friend request"
            )
        ]
        ordering = ["sender", "friend"]