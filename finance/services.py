import pandas as pd
import numpy as np

def process_and_analyze_stock(raw_qs):
    """
    Membersihkan data, memvalidasi OHLC, menangani NaN, 
    serta menghitung indikator teknikal lengkap secara aman.
    """
    if not raw_qs.exists():
        return None, None

    # Konversi queryset ke Pandas DataFrame
    df = pd.DataFrame(list(raw_qs.values(
        'date', 'open_price', 'high_price', 'low_price', 'close_price', 'volume'
    )))

    if df.empty:
        return None, None

    # Pastikan urutan tanggal benar (ascending untuk kalkulasi indikator)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date').reset_index(drop=True)

    # Validasi & konversi tipe numerik, tangani NaN (forward fill / backward fill)
    cols = ['open_price', 'high_price', 'low_price', 'close_price', 'volume']
    for c in cols:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    
    df.dropna(subset=['close_price'], inplace=True)
    df[cols] = df[cols].ffill().bfill()

    close = df['close_price']
    high = df['high_price']
    low = df['low_price']
    vol = df['volume']

    # --- 1. Moving Averages & EMA (Aman jika data < periode berkat min_periods=1) ---
    df['sma_5'] = close.rolling(window=5, min_periods=1).mean()
    df['sma_20'] = close.rolling(window=20, min_periods=1).mean()
    df['ema_9'] = close.ewm(span=9, adjust=False).mean()
    df['ema_21'] = close.ewm(span=21, adjust=False).mean()

    # --- 2. Bollinger Bands (20, 2) ---
    r_std = close.rolling(window=20, min_periods=1).std().fillna(0)
    df['bb_upper'] = df['sma_20'] + (r_std * 2)
    df['bb_lower'] = df['sma_20'] - (r_std * 2)

    # --- 3. RSI 14 ---
    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14, min_periods=1).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14, min_periods=1).mean()
    rs = gain / (loss.replace(0, 0.001))
    df['rsi_14'] = 100 - (100 / (1 + rs))

    # --- 4. MACD & Signal ---
    exp12 = close.ewm(span=12, adjust=False).mean()
    exp26 = close.ewm(span=26, adjust=False).mean()
    df['macd'] = exp12 - exp26
    df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()

    # --- 5. Volume MA ---
    df['volume_ma20'] = vol.rolling(window=20, min_periods=1).mean()

    # --- 6. Support & Resistance (30D High/Low) ---
    support = low.min()
    resistance = high.max()

    # --- 7. Sinyal, Skor & Alasan (Bullish/Bearish/Neutral) ---
    latest = df.iloc[-1]
    score = 50
    reasons = []

    # Harga vs SMA20
    if latest['close_price'] > latest['sma_20']:
        reasons.append(f"Harga di atas SMA 20 ({latest['close_price']:.0f} > {latest['sma_20']:.0f})")
        score += 15
    else:
        reasons.append("Harga di bawah SMA 20")
        score -= 15

    # RSI
    rsi_val = latest['rsi_14']
    if rsi_val > 55:
        reasons.append(f"RSI menunjukkan momentum beli ({rsi_val:.1f})")
        score += 10
    elif rsi_val < 45:
        reasons.append(f"RSI menunjukkan tekanan jual ({rsi_val:.1f})")
        score -= 10
    else:
        reasons.append(f"RSI berada di zona netral ({rsi_val:.1f})")

    # MACD
    if latest['macd'] > latest['macd_signal']:
        reasons.append("Garis MACD berada di atas sinyal (Positif)")
        score += 15
    else:
        reasons.append("MACD berada di bawah garis sinyal (Negatif)")
        score -= 15

    # Volume vs Volume MA
    if latest['volume'] > latest['volume_ma20']:
        reasons.append("Volume transaksi harian di atas rata-rata 20 hari")
        score += 10

    # Batasi skor 0 - 100
    score = int(max(0, min(100, score)))
    if score >= 65:
        status, badge = "Bullish", "success"
    elif score <= 35:
        status, badge = "Bearish", "danger"
    else:
        status, badge = "Neutral", "secondary"

    analytics = {
        "status": status,
        "badge": badge,
        "score": score,
        "reasons": reasons,
        "rsi": round(rsi_val, 2),
        "support": support,
        "resistance": resistance,
    }

    return df, analytics