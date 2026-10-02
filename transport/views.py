from django.http import JsonResponse
from .models import TransportStock

def get_transport_stock(request, ticker):
    """Mengambil data OHLC saham sektor transportasi dan logistik."""
    stocks = TransportStock.objects.filter(ticker=ticker.upper())[:30]
    data = [{
        "date": stock.date.strftime("%Y-%m-%d"),
        "open": float(stock.open_price),
        "high": float(stock.high_price),
        "low": float(stock.low_price),
        "close": float(stock.close_price),
        "volume": stock.volume
    } for stock in stocks]
    
    return JsonResponse({"ticker": ticker.upper(), "sector": "Transportation & Logistics", "data": data})
