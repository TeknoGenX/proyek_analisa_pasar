from django.http import JsonResponse
from .models import ForexData

def get_forex_pair(request, pair):
    """Mengambil 50 data histori terakhir untuk pair tertentu."""
    data = ForexData.objects.filter(pair=pair.upper())[:50]
    result = [{
        "timestamp": item.timestamp.isoformat(),
        "bid": float(item.bid_price),
        "ask": float(item.ask_price)
    } for item in data]
    
    return JsonResponse({"pair": pair.upper(), "data": result})