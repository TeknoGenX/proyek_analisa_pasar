from django.http import JsonResponse
from .models import PropertyStock

def get_property_stock(request, ticker):
    """Mengambil data OHLC saham sektor properti dan real estat."""
    stocks = PropertyStock.objects.filter(ticker=ticker.upper())[:30]
    data = [{
        "date": stock.date.strftime("%Y-%m-%d"),
        "open": float(stock.open_price),
        "high": float(stock.high_price),
        "low": float(stock.low_price),
        "close": float(stock.close_price),
        "volume": stock.volume
    } for stock in stocks]
    
    return JsonResponse({"ticker": ticker.upper(), "sector": "Property & Real Estate", "data": data})
