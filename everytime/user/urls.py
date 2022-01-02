from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import UserSignUpView, UserLoginView, google_login, google_callback, VerifyingMailSendView, VerifyingMailAcceptView, SocialUserSignUpView
from . import views

app_name='user'

urlpatterns = [
    path('signup/', UserSignUpView.as_view(), name='signup'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('google/login/', google_login, name='google_login'),
    path('google/login/callback/', google_callback,  name='google_callback'),
    path('verify/send/', VerifyingMailSendView.as_view(), name='email_verify_send'),
    path('verify/accepted/<str:uidb64>/<str:token>/<str:emailb64>/', VerifyingMailAcceptView.as_view(), name='email_verify_send'),
    path('social/signup/', SocialUserSignUpView.as_view(), name='social_signup'),
    path('naver/login/', views.naver_login, name='naver_login'),
    path('naver/login/callback/', views.naver_callback, name='naver_callback'),
]