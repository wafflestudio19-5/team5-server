from django.urls import path, include

from rest_framework.routers import SimpleRouter
from . import views


app_name='user'
urlpatterns = [
    path('signup/', views.UserSignUpView.as_view(), name='signup'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('kakao/login/', views.KaKaoLoginView.as_view(), name='kakao login'),
    path('kakao/callback/', views.kakao_callback, name='kakao callback'),
    path('google/login/', views.GoogleLoginView.as_view(), name='google_login'),
    path('google/login/callback/', views.google_callback,  name='google_callback'),
    path('social/signup/', views.SocialUserSignUpView.as_view(), name='social_signup'),
    path('naver/login/', views.NaverLoginView.as_view(), name='naver_login'),
    path('naver/login/callback/', views.naver_callback, name='naver_callback'),
    path('verify/send/', views.VerifyingMailSendView.as_view(), name='email_verify_send'),
    path('verify/accepted/<str:uidb64>/<str:token>/<str:emailb64>/', views.VerifyingMailAcceptView.as_view(),
         name='email_verify_accept'),
]