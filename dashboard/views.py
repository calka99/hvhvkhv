from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from rest_framework.response import Response

from dashboard.models import Dashboard
from dashboard.serializers import DashboardSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_overview(request):
    dashboard = Dashboard.objects.filter(owner=request.user).order_by('-updated_at').first()

    if dashboard is None:
        return Response({'detail': 'No dashboard available.'}, status=404)

    serializer = DashboardSerializer(dashboard)
    return Response(serializer.data)

