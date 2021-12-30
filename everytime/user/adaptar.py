from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from user.models import User
from user.serializers import UserCreateSerializer


# class SocialAccountRegisterAdapter(DefaultSocialAccountAdapter):
#     def pre_social_login(self, request, sociallogin):
#         if sociallogin.user.id:
#             return
#         if request.user and request.user.is_authenticated:
#             try:
#                 login_user = User.objects.get(email=request.user)
#                 sociallogin.connect(request, login_user)
#             except User.DoesNotExist:
#                 pass
#
#     def save_user(self, request, sociallogin, form=None):
#         serializer = UserCreateSerializer(data=request.POST)
#         serializer.is_valid()
#
#         user = super().save_user(request, sociallogin, form)
#         return user
