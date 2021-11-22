from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import UserSignUpView, UserLoginView

router = SimpleRouter()
# router.register('signup', UserSignUpView, basename='signup')

urlpatterns = [
    path('signup/', UserSignUpView.as_view(), name='signup'),
    path('login/', UserLoginView.as_view(), name='login'),
    # path('', include(router.urls), name='auth-user')
]