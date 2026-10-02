import time
import logging
import pandas as pd
import yfinance as yf
from decimal import Decimal
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from django.core.management.base import BaseCommand
from django.db import transaction, IntegrityError
from django.utils.timezone import make_aware, is_naive

# Import Model 12 Sektor (Lengkap tanpa terlewat)
from basic_idn.models import BasicIndustryStock
from cyclical.models import CyclicalStock
from energy.models import EnergyStock
from finance.models import FinanceStock
from forex.models import ForexCandle
from health.models import HealthStock
from industrial.models import IndustrialStock
from infrastructure.models import InfrastructureStock
from non_cyclical.models import NonCyclicalStock
from property.models import PropertyStock
from technology.models import TechnologyStock
from transport.models import TransportStock

logger = logging.getLogger(__name__)

# Mapping 11 Sektor Saham
TICKER_MAP = {
    'BBCA': FinanceStock, 'BBRI': FinanceStock, 'BMRI': FinanceStock, 'BBNI': FinanceStock,
    'ADRO': EnergyStock, 'MEDC': EnergyStock, 'PGAS': EnergyStock, 'PTBA': EnergyStock,
    'ANTM': BasicIndustryStock, 'MDKA': BasicIndustryStock, 'INCO': BasicIndustryStock, 'BRPT': BasicIndustryStock,
    'ACES': CyclicalStock, 'MAPI': CyclicalStock, 'ERAA': CyclicalStock,
    'ICBP': NonCyclicalStock, 'INDF': NonCyclicalStock, 'UNVR': NonCyclicalStock, 'MYOR': NonCyclicalStock,
    'ASII': IndustrialStock, 'UNTR': IndustrialStock, 'HEXA': IndustrialStock,
    'KLBF': HealthStock, 'MIKA': HealthStock, 'SIDO': HealthStock,
    'TLKM': InfrastructureStock, 'ISAT': InfrastructureStock, 'JSMR': InfrastructureStock, 'TOWR': InfrastructureStock,
    'BSDE': PropertyStock, 'CTRA': PropertyStock, 'PWON': PropertyStock, 'SMRA': PropertyStock,
    'GOTO': TechnologyStock, 'BUKA': TechnologyStock, 'EMTK': TechnologyStock,
    'BIRD': TransportStock, 'GIAA': TransportStock, 'ASSA': TransportStock,
}

# Sektor ke-12 (Forex)
FOREX_PAIRS = ['USDIDR', 'EURUSD', 'USDJPY']

def fetch_with_retry(yf_symbol, period, retries=3, backoff_factor=2):
    """
    Mengambil data dari Yahoo Finance dengan mekanisme Retry dan Exponential Backoff.
    Mencegah script crash jika terjadi timeout atau rate-limiting sementara.
    """
    for attempt in range(retries):
        try:
            t = yf.Ticker(yf_symbol)
            df = t.history(period=period)
            
            # Validasi jika data kosong
            if df.empty:
                return pd.DataFrame()
            
            # Sanitasi Data Pandas (Pembersihan NaN)
            df = df.fillna(0)
            return df
            
        except Exception as e:
            if attempt == retries - 1:
                logger.error(f"Gagal mengambil {yf_symbol} setelah {retries} percobaan: {e}")
                raise e
            time.sleep(backoff_factor ** attempt)
    return pd.DataFrame()

def sync_stock_ticker(ticker, period='1mo'):
    """Logika pemrosesan data historis saham dengan transaksi atomik."""
    ticker_clean = ticker.upper().strip()
    model_cls = TICKER_MAP.get(ticker_clean, FinanceStock) # Fallback aman
    yf_symbol = f"{ticker_clean}.JK"

    df = fetch_with_retry(yf_symbol, period)
    if df.empty:
        return 0

    inserted_count = 0
    # Membungkus operasi database dalam transaksi atomik untuk integritas data
    with transaction.atomic():
        for idx, row in df.iterrows():
            trade_date = idx.date() if hasattr(idx, 'date') else idx
            
            # Skip jika volume 0 (hari libur bursa tetapi ter-record API)
            if int(row.get('Volume', 0)) == 0:
                continue

            model_cls.objects.update_or_create(
                ticker=ticker_clean,
                date=trade_date,
                defaults={
                    'open_price': Decimal(str(round(row['Open'], 2))),
                    'high_price': Decimal(str(round(row['High'], 2))),
                    'low_price': Decimal(str(round(row['Low'], 2))),
                    'close_price': Decimal(str(round(row['Close'], 2))),
                    'volume': int(row['Volume']),
                }
            )
            inserted_count += 1

    return inserted_count

def sync_forex_pair(pair, period='1mo'):
    """Logika pemrosesan data forex intra-day dengan penanganan Timezone yang ketat."""
    pair_clean = pair.upper().strip()
    yf_symbol = f"{pair_clean}=X"
    
    df = fetch_with_retry(yf_symbol, period)
    if df.empty:
        return 0

    inserted_count = 0
    with transaction.atomic():
        for idx, row in df.iterrows():
            ts = idx.to_pydatetime()
            # Memastikan timestamp sadar zona waktu (Timezone Aware) untuk PostgreSQL/SQLite
            if is_naive(ts):
                ts = make_aware(ts)

            ForexCandle.objects.update_or_create(
                pair=pair_clean,
                timestamp=ts,
                defaults={
                    'bid_price': Decimal(str(round(row['Close'], 5))),
                    'ask_price': Decimal(str(round(row['High'], 5))),
                    'volume': int(row.get('Volume', 0)),
                }
            )
            inserted_count += 1
            
    return inserted_count

class Command(BaseCommand):
    help = 'Sinkronisasi Multithread data harga real-time dari Yahoo Finance'

    def add_arguments(self, parser):
        parser.add_argument('--ticker', type=str, help='Ticker tunggal (misal: BBCA atau USDIDR)')
        parser.add_argument('--period', type=str, default='1mo', help='Periode data (1d, 5d, 1mo, 3mo, 1y)')
        parser.add_argument('--workers', type=int, default=5, help='Jumlah maksimal thread paralel')

    def process_single(self, target, period):
        """Routing untuk tipe aset tunggal."""
        if target in FOREX_PAIRS or '=X' in target:
            clean_pair = target.replace('=X', '')
            count = sync_forex_pair(clean_pair, period)
            return f"Forex {clean_pair}: {count} baris."
        else:
            count = sync_stock_ticker(target, period)
            return f"Saham {target}: {count} baris."

    def handle(self, *args, **options):
        target_ticker = options.get('ticker')
        period = options.get('period', '1mo')
        max_workers = options.get('workers', 5)

        start_time = time.time()

        if target_ticker:
            target = target_ticker.upper()
            try:
                result_msg = self.process_single(target, period)
                self.stdout.write(self.style.SUCCESS(f"✔ Berhasil: {result_msg}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"✖ Gagal sinkronisasi {target}: {e}"))
        else:
            self.stdout.write(self.style.WARNING(f"Memulai sinkronisasi massal dengan {max_workers} thread paralel..."))
            
            # Menyiapkan antrean tugas (Saham + Forex)
            tasks = [(ticker, 'stock') for ticker in TICKER_MAP.keys()]
            tasks.extend([(pair, 'forex') for pair in FOREX_PAIRS])
            
            success_count = 0
            fail_count = 0

            # Eksekusi paralel menggunakan ThreadPoolExecutor untuk I/O Bound Tasks
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Mapping tugas ke executor
                future_to_task = {
                    executor.submit(sync_stock_ticker if t_type == 'stock' else sync_forex_pair, item, period): item 
                    for item, t_type in tasks
                }

                for future in as_completed(future_to_task):
                    item = future_to_task[future]
                    try:
                        count = future.result()
                        self.stdout.write(self.style.SUCCESS(f"  [+] {item} terekstraksi ({count} baris)"))
                        success_count += 1
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"  [-] {item} gagal: {str(e)}"))
                        fail_count += 1

            elapsed = round(time.time() - start_time, 2)
            self.stdout.write(self.style.WARNING("\n=== Laporan Eksekusi ETL ==="))
            self.stdout.write(f"Durasi: {elapsed} detik")
            self.stdout.write(self.style.SUCCESS(f"Berhasil: {success_count} instrumen"))
            
            if fail_count > 0:
                self.stdout.write(self.style.ERROR(f"Gagal: {fail_count} instrumen (Periksa koneksi/rate-limit)"))