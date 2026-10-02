from django.http import JsonResponse
from .models import InfrastructureStock

def get_infrastructure_stock(request, ticker):
    """Mengambil data OHLC saham sektor infrastruktur (Infrastructure)."""
    stocks = InfrastructureStock.objects.filter(ticker=ticker.upper())[:30]
    data = [{
        "date": stock.date.strftime("%Y-%m-%d"),
        "open": float(stock.open_price),
        "high": float(stock.high_price),
        "low": float(stock.low_price),
        "close": float(stock.close_price),
        "volume": stock.volume
    } for stock in stocks]
    
    return JsonResponse({"ticker": ticker.upper(), "sector": "Infrastructure", "data": data})
