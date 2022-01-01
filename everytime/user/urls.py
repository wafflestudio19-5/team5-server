from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import UserSignUpView, UserLoginView, google_login, google_callback

router = SimpleRouter()
# router.register('signup', UserSignUpView, basename='signup')

urlpatterns = [
    path('signup/', UserSignUpView.as_view(), name='signup'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('google/login/', google_login, name='google_login'),
    path('google/login/callback/', google_callback,  name='google_callback'),
    # path('', include(router.urls), name='auth-user')
]