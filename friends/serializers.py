from rest_framework import serializers
from .models import FriendRequest
from users.serializers import UserSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class FriendRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = ('id', 'from_user', 'to_user', 'status', 'created_at')
        read_only_fields = ('from_user', 'created_at')

class FriendListSerializer(serializers.ModelSerializer):
    friend = serializers.SerializerMethodField()

    class Meta:
        model = FriendRequest
        fields = ('id', 'friend', 'created_at')

    def get_friend(self, obj):
        request = self.context.get('request')
        if obj.from_user == request.user:
            return UserSerializer(obj.to_user).data
        return UserSerializer(obj.from_user).data