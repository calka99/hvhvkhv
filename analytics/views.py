from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.decorators import api_view, permission_classes

from farm_overview.models import AnalyticsSnapshot
from .serializers import AnalyticsSnapshotSerializer


# Analytics Views

@api_view(['GET'])
def list_analytics(request):
    farm_id = request.query_params.get('farm_id')
    analytics = AnalyticsSnapshot.objects.all()
    if farm_id:
        analytics = analytics.filter(farm_id=farm_id)
    analytics = analytics.order_by('-id')
    serializer = AnalyticsSnapshotSerializer(analytics, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def create_analytics(request):
    serializer = AnalyticsSnapshotSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    analytics = serializer.save()
    out = AnalyticsSnapshotSerializer(analytics)
    return Response(out.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def get_analytics(request, analytics_id):
    analytics = get_object_or_404(AnalyticsSnapshot, pk=analytics_id)
    serializer = AnalyticsSnapshotSerializer(analytics)
    return Response(serializer.data)


@api_view(['PUT'])
@permission_classes([IsAdminUser])
def update_analytics(request, analytics_id):
    analytics = get_object_or_404(AnalyticsSnapshot, pk=analytics_id)
    serializer = AnalyticsSnapshotSerializer(analytics, data=request.data, partial=True)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    serializer.save()
    return Response(serializer.data)


@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def delete_analytics(request, analytics_id):
    analytics = get_object_or_404(AnalyticsSnapshot, pk=analytics_id)
    analytics.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
