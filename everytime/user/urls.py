from django.urls import path, include
from . import views
from .views import UserSignUpView, UserLoginView, SocialUserSignUpView

app_name='user'

urlpatterns = [
    path('signup/', UserSignUpView.as_view(), name='signup'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('social/signup/', SocialUserSignUpView.as_view(), name='social_signup'),
    path('naver/login/', views.naver_login, name='naver_login'),
    path('naver/login/callback/', views.naver_callback, name='naver_callback'),
]