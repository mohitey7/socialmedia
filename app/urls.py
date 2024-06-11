from django.urls import path
from .views import *

urlpatterns = [
    path('signup/', UserSignup.as_view()),
    path('login/', UserLogin.as_view()),
    path('logout/', UserLogout.as_view()),
    path('search/', UserSearch.as_view()),
    path('send-request/', FriendRequestView.as_view()),
    path('action-request/', FriendRequestAction.as_view()),
    path('requests/', PendingRequests.as_view()),
    path('friend-list/', FriendList.as_view())
]