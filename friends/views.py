from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
from .models import FriendRequest
from django.contrib.auth import get_user_model
from .serializers import *
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class SendFriendRequestView(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(request_body=FriendRequestSerializer)
    def post(self, request):
        serializer = FriendRequestSerializer(data=request.data)
        if serializer.is_valid():
            from_user = request.user
            to_user = serializer.validated_data['to_user']

            friend_request = FriendRequest.objects.filter((Q(from_user = from_user) and Q(to_user = to_user)) | (Q(from_user = to_user) and Q(to_user = from_user)))
            if friend_request.exists():
                return Response({"error": "You both are friends."}, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if user has sent more than 3 requests in the last minute
            one_minute_ago = timezone.now() - timedelta(minutes=1)
            recent_requests = FriendRequest.objects.filter(from_user=from_user, created_at__gte=one_minute_ago).count()
            
            if recent_requests >= 3:
                return Response({"error": "You can't send more than 3 friend requests within a minute."}, 
                                status=status.HTTP_400_BAD_REQUEST)
            
            friend_request = serializer.save(from_user=from_user, to_user=to_user)
            return Response(FriendRequestSerializer(friend_request).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AcceptRejectFriendRequestView(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(request_body=ManageFriendRequestSerializer)
    def put(self, request):
        serializer = ManageFriendRequestSerializer(data=request.data)
        if serializer.is_valid():
            id = serializer.validated_data['id']
            try:
                friend_request = FriendRequest.objects.get(pk=id)
            except FriendRequest.DoesNotExist:
                return Response({"error": "Friend request not found."}, status=status.HTTP_404_NOT_FOUND)

            if friend_request.to_user != request.user:
                return Response({"error": "You don't have permission to perform this action."}, 
                                status=status.HTTP_403_FORBIDDEN)
            friend_request.status = serializer.validated_data['status']
            friend_request.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class FriendListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        friend_requests = FriendRequest.objects.filter(
            (Q(from_user=request.user) | Q(to_user=request.user)) & Q(status='accepted')
        )
        serializer = FriendListSerializer(friend_requests, many=True, context={'request': request})
        return Response(serializer.data)

class PendingFriendRequestsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        pending_requests = FriendRequest.objects.filter(to_user=request.user, status='pending')
        serializer = FriendRequestSerializer(pending_requests, many=True)
        return Response(serializer.data)