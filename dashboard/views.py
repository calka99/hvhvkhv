from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response

from dashboard.models import Dashboard
from dashboard.serializers import DashboardSerializer


@api_view(['GET'])
def dashboard_overview(request):
    user = getattr(request, 'user', None)

    if user and getattr(user, 'is_authenticated', False):
        dashboard = Dashboard.objects.filter(owner=user).order_by('-updated_at').first()
    else:
        dashboard = None

    if dashboard is None:
        dashboard = Dashboard.objects.order_by('-updated_at').first()

    if dashboard is None:
        if user and getattr(user, 'is_authenticated', False):
            dashboard = Dashboard.objects.create(owner=user, title='My Farm Overview')
        else:
            return Response({'detail': 'No dashboard available.'}, status=404)

    serializer = DashboardSerializer(dashboard)
    return Response(serializer.data)

