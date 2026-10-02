import pandas as pd
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db import transaction

# Import 12 Sektor sesuai arsitektur proyek
from basic_idn.models import BasicIndustryStock
from cyclical.models import CyclicalStock
from energy.models import EnergyStock
from finance.models import FinanceStock
from forex.models import ForexData
from health.models import HealthStock
from industrial.models import IndustrialStock
from infrastructure.models import InfrastructureStock
from non_cyclical.models import NonCyclicalStock
from property.models import PropertyStock
from technology.models import TechnologyStock
from transport.models import TransportStock
from django.utils.timezone import make_aware, is_naive

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
FOREX_PAIRS = ['USDIDR', 'EURUSD', 'USDJPY']

class Command(BaseCommand):
    help = 'Bulk Import data historis saham & forex dari CSV dengan Memory-Safe Chunking'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path ke file CSV')
        parser.add_argument('--ticker', type=str, help='Gunakan jika CSV tidak punya kolom ticker', default=None)
        parser.add_argument('--chunksize', type=int, default=10000, help='Jumlah baris per eksekusi memori')

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']
        override_ticker = kwargs.get('ticker')
        chunk_size = kwargs.get('chunksize')

        self.stdout.write(self.style.WARNING(f'Membaca {csv_file} (Chunk size: {chunk_size})...'))

        total_inserted = 0

        try:
            # Menggunakan chunksize agar RAM tidak jebol saat membaca file CSV bergiga-giga
            df_chunks = pd.read_csv(csv_file, chunksize=chunk_size)

            for chunk_idx, df in enumerate(df_chunks):
                # Normalisasi header CSV
                df.columns = [col.strip().lower() for col in df.columns]
                
                # Membersihkan data null (NaN) menjadi 0
                df = df.fillna(0)

                # Dictionary untuk memisahkan data per model/sektor di dalam chunk ini
                models_to_create = {}

                for index, row in df.iterrows():
                    # Penentuan Ticker
                    raw_ticker = row.get('ticker', override_ticker)
                    if not raw_ticker:
                        continue # Lewati jika tidak ada ticker sama sekali
                        
                    current_ticker = str(raw_ticker).strip().upper()

                    # Penentuan Routing Model (Forex vs Saham)
                    if current_ticker in FOREX_PAIRS or '=X' in current_ticker:
                        model_cls = ForexData
                        current_ticker = current_ticker.replace('=X', '')
                        is_forex = True
                    else:
                        model_cls = TICKER_MAP.get(current_ticker, FinanceStock) # Fallback ke Finance
                        is_forex = False

                    # Inisialisasi list jika model ini belum ada di dictionary
                    if model_cls not in models_to_create:
                        models_to_create[model_cls] = []

                    # Pembuatan Objek
                    try:
                        if is_forex:
                            # Logika spesifik kolom Forex (timestamp, bid, ask)
                            ts = pd.to_datetime(row['timestamp']).to_pydatetime()
                            if is_naive(ts):
                                ts = make_aware(ts)
                            
                            instance = model_cls(
                                pair=current_ticker,
                                timestamp=ts,
                                bid_price=Decimal(str(round(row.get('bid_price', row.get('close', 0)), 5))),
                                ask_price=Decimal(str(round(row.get('ask_price', row.get('high', 0)), 5))),
                                volume=int(row.get('volume', 0))
                            )
                        else:
                            # Logika spesifik kolom Saham (date, OHLC)
                            parsed_date = pd.to_datetime(row['date']).date()
                            
                            instance = model_cls(
                                ticker=current_ticker,
                                date=parsed_date,
                                open_price=Decimal(str(round(row['open'], 2))),
                                high_price=Decimal(str(round(row['high'], 2))),
                                low_price=Decimal(str(round(row['low'], 2))),
                                close_price=Decimal(str(round(row['close'], 2))),
                                volume=int(row.get('volume', 0))
                            )
                            
                        models_to_create[model_cls].append(instance)
                    except Exception as parse_err:
                        self.stdout.write(self.style.ERROR(f"Error parsing baris {index}: {parse_err}"))
                        continue

                # Eksekusi Bulk Create ke database secara per-model dalam satu transaksi atomik
                with transaction.atomic():
                    for model_class, instances in models_to_create.items():
                        if instances:
                            model_class.objects.bulk_create(instances, ignore_conflicts=True)
                            total_inserted += len(instances)

                self.stdout.write(f"  [+] Chunk {chunk_idx + 1} diproses. Subtotal masuk: {total_inserted} baris.")

            self.stdout.write(self.style.SUCCESS(f'\nSUKSES! Total {total_inserted} baris data historis berhasil diimpor ke sektor masing-masing.'))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'Error kritis: File {csv_file} tidak ditemukan di sistem.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Proses impor terhenti karena error sistem: {e}'))