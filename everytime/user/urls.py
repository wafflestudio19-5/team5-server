from django.urls import path, include
from .views import UserSignUpView, UserLoginView


urlpatterns = [
    path('signup/', UserSignUpView.as_view(), name='signup'),
    path('login/', UserLoginView.as_view(), name='login'),
]