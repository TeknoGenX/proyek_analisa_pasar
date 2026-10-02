from datetime import timedelta
from .models import InfrastructureStock

def seed_infrastructure_data(today_date):
    tickers = [('TLKM', 3100), ('ISAT', 9800), ('JSMR', 4800)]
    
    for ticker, base_price in tickers:
        for i in range(5):
            d = today_date - timedelta(days=i)
            InfrastructureStock.objects.get_or_create(
                ticker=ticker, date=d,
                defaults={
                    'open_price': base_price,
                    'high_price': base_price + 60,
                    'low_price': base_price - 40,
                    'close_price': base_price + 20,
                    'volume': 22000000 + i * 1500000
                }
            )