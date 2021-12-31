from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import UserSignUpView, UserLoginView, KaKaoLoginView, kakao_callback

router = SimpleRouter()

app_name='user'
urlpatterns = [
    path('signup/', UserSignUpView.as_view(), name='signup'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('kakao/login/', KaKaoLoginView.as_view(), name='kakao login'),
    path('kakao/callback/', kakao_callback, name='kakao callback')
]