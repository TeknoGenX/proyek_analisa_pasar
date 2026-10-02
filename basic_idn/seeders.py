from datetime import timedelta
from .models import BasicIndustryStock

def seed_basic_industry_data(today_date):
    tickers = [('ANTM', 1500), ('MDKA', 2300), ('INCO', 3900)]
    
    for ticker, base_price in tickers:
        for i in range(5):
            d = today_date - timedelta(days=i)
            BasicIndustryStock.objects.get_or_create(
                ticker=ticker, date=d,
                defaults={
                    'open_price': base_price,
                    'high_price': base_price + 50,
                    'low_price': base_price - 30,
                    'close_price': base_price + 20,
                    'volume': 15000000 + i * 1000000
                }
            )