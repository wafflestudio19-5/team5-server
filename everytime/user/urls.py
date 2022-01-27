from django.urls import path, include

from rest_framework.routers import SimpleRouter
from . import views


app_name='user'
urlpatterns = [
    path('signup/', views.UserSignUpView.as_view(), name='signup'),
    path('deactivate/', views.UserDeleteAccountView.as_view(), name='delete account'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
    path('kakao/login/', views.KaKaoLoginView.as_view(), name='kakao login'),
    path('kakao/login/callback/', views.kakao_callback, name='kakao callback'),
    path('google/login/', views.GoogleLoginView.as_view(), name='google_login'),
    path('google/login/callback/', views.google_callback,  name='google_callback'),
    path('social/signup/', views.SocialUserSignUpView.as_view(), name='social_signup'),
    path('naver/login/', views.NaverLoginView.as_view(), name='naver_login'),
    path('naver/login/callback/', views.naver_callback, name='naver_callback'),
    path('verify/send/', views.VerifyingMailSendView.as_view(), name='email_verify_send'),
    path('verify/accepted/<str:uidb64>/<str:token>/<str:emailb64>/', views.VerifyingMailAcceptView.as_view(),
         name='email_verify_accept'),
    path('myscrap/', views.UserScrapView.as_view(), name='myscrap'),
    path('mypost/', views.UserPostView.as_view(), name='myscrap'),
    path('mycomment/', views.UserCommentView.as_view(), name='myscrap'),
    path('myprofile/', views.UserProfileView.as_view(), name='myprofile'),
    path('issocial/', views.IsSocialView.as_view(), name='is_social'),
    path('social/deactivate/', views.SocialUserDeleteAccountView.as_view(), name='delete social account'),
    path('naver/deactivate/callback/', views.naver_delete_callback, name = 'naver delete callback'),
    path('kakao/deactivate/callback/', views.kakao_delete_callback, name = 'kakao delete callback'),
    path('google/deactivate/callback/', views.google_delete_callback, name = 'google delete callback'),
]