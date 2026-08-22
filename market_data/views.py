from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from farm_overview.models import MarketPrice
from .serializers import MarketPriceSerializer


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def market_prices(request):
	if request.method == 'GET':
		prices = MarketPrice.objects.all().order_by('-recorded_at', 'commodity')
		return Response(MarketPriceSerializer(prices, many=True).data)

	if not request.user.is_staff:
		return Response({'detail': 'Only administrators can add market data.'}, status=status.HTTP_403_FORBIDDEN)

	serializer = MarketPriceSerializer(data=request.data)
	serializer.is_valid(raise_exception=True)
	price = serializer.save()
	return Response(MarketPriceSerializer(price).data, status=status.HTTP_201_CREATED)
