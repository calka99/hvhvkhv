from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from .models import FarmPreference
from .serializers import FarmPreferenceSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_settings(request):
    preference, _ = FarmPreference.objects.get_or_create(owner=request.user)
    return Response(FarmPreferenceSerializer(preference).data)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_settings(request):
    preference, _ = FarmPreference.objects.get_or_create(owner=request.user)
    serializer = FarmPreferenceSerializer(preference, data=request.data, partial=True)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    serializer.save()
    return Response(serializer.data)
