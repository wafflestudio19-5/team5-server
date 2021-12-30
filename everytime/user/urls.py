from django.urls import path, include
from . import views
from .views import UserSignUpView, UserLoginView, NaverLogin

urlpatterns = [
    path('signup/', UserSignUpView.as_view(), name='signup'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('naver/login/', views.naver_login, name='naver_login'),
    path('naver/callback/', views.naver_callback, name='naver_callback'),
    path('naver/login/finish/', views.NaverLogin.as_view(), name='naver_login_todjango'),
]