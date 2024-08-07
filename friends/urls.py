from django.urls import path
from .views import SendFriendRequestView, AcceptRejectFriendRequestView, FriendListView, PendingFriendRequestsView

urlpatterns = [
    path('send-request/', SendFriendRequestView.as_view(), name='send-friend-request'),
    path('handle-request/<int:pk>/', AcceptRejectFriendRequestView.as_view(), name='handle-friend-request'),
    path('list/', FriendListView.as_view(), name='friend-list'),
    path('pending-requests/', PendingFriendRequestsView.as_view(), name='pending-friend-requests'),
]