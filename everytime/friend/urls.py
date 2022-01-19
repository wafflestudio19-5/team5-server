from django.urls import path
from . import views


urlpatterns = [
    path('', views.FriendListView.as_view(), name='Friend list'),
    path('<int:pk>/', views.FriendView.as_view(), name='Accept friend'),
    path('request/', views.FriendRequestView.as_view(), name='Request friend'),
    path('request/<int:pk>/', views.FriendRequestDeleteView.as_view(), name='Delete Request')
]