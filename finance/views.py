from django.http import JsonResponse
from django.shortcuts import redirect
from .models import FinanceStock

def get_finance_stock(request, ticker):
    """Mengambil data OHLC saham sektor keuangan."""
    stocks = FinanceStock.objects.filter(ticker=ticker.upper())[:30]
    data = [{
        "date": stock.date.strftime("%Y-%m-%d"),
        "open": float(stock.open_price),
        "high": float(stock.high_price),
        "low": float(stock.low_price),
        "close": float(stock.close_price),
        "volume": stock.volume
    } for stock in stocks]
    
    return JsonResponse({"ticker": ticker.upper(), "sector": "Finance", "data": data})

def finance_web_dashboard(request, ticker):
    """Mengarahkan ke universal visual dashboard saham."""
    return redirect('stock_dashboard', ticker=ticker.upper())