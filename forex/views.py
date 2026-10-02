# forex/views.py
from django.http import JsonResponse
from .models import ForexCandle

def get_forex_pair(request, pair):
    """Mengambil 50 data candle histori terakhir untuk pair tertentu."""
    timeframe = request.GET.get('timeframe', 'H4') # Bisa difilter via query param (?timeframe=H1)
    
    data = ForexCandle.objects.filter(
        pair=pair.upper(), 
        timeframe=timeframe
    )[:50]
    
    result = [{
        "timestamp": item.timestamp.isoformat(),
        "open": float(item.open_price),
        "high": float(item.high_price),
        "low": float(item.low_price),
        "close": float(item.close_price),
        "volume": item.volume
    } for item in data]
    
    return JsonResponse({"pair": pair.upper(), "timeframe": timeframe, "data": result})