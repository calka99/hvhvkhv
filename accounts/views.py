from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    RegisterSerializer,
    UserProfileSerializer,
    UserProfileUpdateSerializer,
)

User = get_user_model()


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    user = serializer.save()
    refresh = RefreshToken.for_user(user)

    return Response(
        {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserProfileSerializer(user).data,
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    identifier = request.data.get('username') or request.data.get('email')
    password = request.data.get('password')

    if not identifier or not password:
        return Response(
            {'detail': 'Username/email and password are required.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = None
    if '@' in identifier:
        user = User.objects.filter(email__iexact=identifier).first()
    else:
        user = User.objects.filter(username__iexact=identifier).first()

    if user is None or not user.check_password(password):
        return Response(
            {'detail': 'Invalid username/email or password.'},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    if not user.is_active:
        return Response(
            {'detail': 'This user account is disabled.'},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    refresh = RefreshToken.for_user(user)
    return Response(
        {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserProfileSerializer(user).data,
        }
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
    serializer = UserProfileSerializer(request.user)
    return Response(serializer.data)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    serializer = UserProfileUpdateSerializer(request.user, data=request.data, partial=True)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    serializer.save()
    return Response(UserProfileSerializer(request.user).data)
