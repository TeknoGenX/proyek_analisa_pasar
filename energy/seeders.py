from datetime import timedelta
from .models import EnergyStock

def seed_energy_data(today_date):
    tickers = [('ADRO', 3600), ('MEDC', 1250), ('PGAS', 1500)]
    
    for ticker, base_price in tickers:
        for i in range(5):
            d = today_date - timedelta(days=i)
            EnergyStock.objects.get_or_create(
                ticker=ticker, date=d,
                defaults={
                    'open_price': base_price,
                    'high_price': base_price + 70,
                    'low_price': base_price - 40,
                    'close_price': base_price + 30,
                    'volume': 25000000 + i * 2000000
                }
            )