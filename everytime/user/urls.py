from django.urls import path, include
from rest_framework.routers import SimpleRouter
from . import views
from .views import UserSignUpView, UserLoginView

router = SimpleRouter()
# router.register('signup', UserSignUpView, basename='signup')

urlpatterns = [
    path('signup/', UserSignUpView.as_view(), name='signup'),
    path('login/', UserLoginView.as_view(), name='login'),
    # path('naver/login', views.naver_login, name='naver_login'),
    # path('naver/callback/', views.naver_callback, name='naver_callback'),
]