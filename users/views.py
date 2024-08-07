from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.contrib.auth import get_user_model, authenticate
from .serializers import UserSerializer, LoginSerializer, UserSearchSerializer
from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from oauth2_provider.models import Application, AccessToken
from oauth2_provider.generators import generate_client_id, generate_client_secret
from oauth2_provider.settings import oauth2_settings
from oauthlib import common
from django.utils import timezone
from datetime import timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated

User = get_user_model()

class UserSignUpView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=UserSerializer)
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                UserSerializer(user).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=LoginSerializer)
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = authenticate(
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password']
        )
        
        if user is None:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Get or create OAuth2 data
        app, created = Application.objects.get_or_create(
            user=user,
            defaults={
                'client_type': Application.CLIENT_CONFIDENTIAL,
                'authorization_grant_type': Application.GRANT_PASSWORD,
                'name': f'AutoCreatedApp_{user.email}',
                'client_id': generate_client_id(),
                'client_secret': generate_client_secret(),
            }
        )
        
        # Generate token
        expires = timezone.now() + timedelta(seconds=oauth2_settings.ACCESS_TOKEN_EXPIRE_SECONDS)
        scopes = oauth2_settings.SCOPES
        
        access_token = AccessToken.objects.create(
            user=user,
            application=app,
            expires=expires,
            token=common.generate_token(),
            scope=' '.join(scopes)
        )
        
        return Response({
            'access_token': access_token.token,
            'expires_in': oauth2_settings.ACCESS_TOKEN_EXPIRE_SECONDS,
            'token_type': 'Bearer',
            'scope': access_token.scope,
        }, status=status.HTTP_200_OK)
    

class UserSearchView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(query_serializer=UserSearchSerializer)
    def post(self, request):
        serializer = UserSearchSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        query = serializer.validated_data.get('search', '')
        users = User.objects.filter(
            Q(email__iexact=query) | 
            Q(first_name__icontains=query) | 
            Q(last_name__icontains=query)
        ).exclude(id=request.user.id)

        user_serializer = UserSerializer(users, many=True)
        return Response(user_serializer.data, status=status.HTTP_200_OK)