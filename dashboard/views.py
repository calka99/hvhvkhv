from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from rest_framework.response import Response

from dashboard.models import Dashboard
from dashboard.serializers import DashboardSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_overview(request):
    dashboard, _ = Dashboard.objects.get_or_create(owner=request.user)

    serializer = DashboardSerializer(dashboard)
    return Response(serializer.data)

