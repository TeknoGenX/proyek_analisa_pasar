import numpy as np
import pandas as pd

def calculate_technical_indicators(stocks):
    """
    Menghitung indikator teknikal: SMA 5, SMA 20, Bollinger Bands, RSI 14, dan Sinyal Tren.
    Menerima list objek stock Django (diurutkan kronologis tanggal naik).
    """
    if not stocks or len(stocks) < 2:
        return {
            'sma_5': [],
            'sma_20': [],
            'ema_9': [],
            'bb_upper': [],
            'bb_lower': [],
            'rsi': None,
            'rsi_signal': 'Data Tidak Cukup',
            'rsi_badge': 'secondary',
            'trend_signal': 'Netral',
            'trend_badge': 'secondary',
            'support': None,
            'resistance': None,
            'recommendation': {
                'action': 'HOLD / WAIT',
                'action_id': 'DATA TIDAK CUKUP',
                'badge': 'secondary',
                'icon': 'bi-info-circle-fill',
                'score': 50,
                'status': 'Neutral',
                'entry_range': '-',
                'tp1': 0,
                'tp1_pct': 0,
                'tp2': 0,
                'tp2_pct': 0,
                'stop_loss': 0,
                'sl_pct': 0,
                'risk_reward': '-',
                'reasons': ['Data histori kurang dari 2 hari bursa untuk kalkulasi sinyal beli/jual.'],
                'strategy': 'Diperlukan lebih banyak data transaksi untuk memetakan sinyal beli dan jual.',
            }
        }

    # Urutkan kronologis tanggal naik
    sorted_stocks = sorted(stocks, key=lambda s: s.date)
    closes = pd.Series([float(s.close_price) for s in sorted_stocks])
    highs = pd.Series([float(s.high_price) for s in sorted_stocks])
    lows = pd.Series([float(s.low_price) for s in sorted_stocks])
    volumes = pd.Series([float(getattr(s, 'volume', 0)) for s in sorted_stocks])

    # 1. Moving Averages (SMA & EMA)
    sma_5_series = closes.rolling(window=min(5, len(closes)), min_periods=1).mean()
    sma_20_series = closes.rolling(window=min(20, len(closes)), min_periods=1).mean()
    ema_9_series = closes.ewm(span=min(9, len(closes)), adjust=False).mean()

    # 2. Bollinger Bands (20 periods, 2 std dev)
    std_20 = closes.rolling(window=min(20, len(closes)), min_periods=1).std().fillna(0)
    bb_upper = sma_20_series + (2 * std_20)
    bb_lower = sma_20_series - (2 * std_20)

    # 3. RSI (Relative Strength Index) 14 periode
    delta = closes.diff()
    gain = delta.clip(lower=0)
    loss = -1 * delta.clip(upper=0)
    window = min(14, max(2, len(closes) - 1))
    avg_gain = gain.rolling(window=window, min_periods=1).mean()
    avg_loss = loss.rolling(window=window, min_periods=1).mean()
    
    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi_series = 100.0 - (100.0 / (1.0 + rs))
    # Tangani kondisi avg_loss == 0 dengan 100.0 jika ada gain, atau 50.0 jika flat
    rsi_series = rsi_series.mask((avg_loss == 0) & (avg_gain > 0), 100.0)
    rsi_series = rsi_series.mask((avg_loss == 0) & (avg_gain == 0), 50.0)
    rsi_series = rsi_series.fillna(50.0)
    
    current_rsi = round(float(rsi_series.iloc[-1]), 1)
    
    if current_rsi >= 70:
        rsi_signal = 'Overbought (Jenuh Beli)'
        rsi_badge = 'danger'
    elif current_rsi <= 30:
        rsi_signal = 'Oversold (Jenuh Jual / Peluang Beli)'
        rsi_badge = 'success'
    else:
        rsi_signal = 'Netral'
        rsi_badge = 'info'

    # 4. Tren Sinyal (Harga saat ini vs SMA)
    current_price = closes.iloc[-1]
    current_sma20 = sma_20_series.iloc[-1]
    current_sma5 = sma_5_series.iloc[-1]

    if current_price > current_sma20 and current_sma5 >= current_sma20:
        trend_signal = 'Bullish (Tren Menguat)'
        trend_badge = 'success'
    elif current_price < current_sma20 and current_sma5 <= current_sma20:
        trend_signal = 'Bearish (Tren Melemah)'
        trend_badge = 'danger'
    else:
        trend_signal = 'Konsolidasi / Sideways'
        trend_badge = 'warning'

    # Support & Resistance
    support = round(float(lows.min()), 2)
    resistance = round(float(highs.max()), 2)

    # 5. Mesin Sinyal Trading & Rekomendasi Eksekusi Beli / Jual
    score = 50
    reasons = []

    # Analisa Tren SMA 20
    if current_price > current_sma20:
        score += 15
        reasons.append(f"Tren Utama Positif: Harga (Rp {int(current_price):,}) bertengger di atas batas Moving Average 20 hari (Rp {int(current_sma20):,}).")
    else:
        score -= 15
        reasons.append(f"Tren Melemah: Harga berada di bawah SMA 20 (Rp {int(current_sma20):,}), menunjukkan tekanan jual jangka menengah.")

    # Analisa Crossover SMA 5 vs SMA 20
    if current_sma5 > current_sma20:
        score += 15
        reasons.append("Momentum Menguat: SMA 5 berada di atas SMA 20 (Kondisi Golden Cross aktif).")
    else:
        score -= 15
        reasons.append("Momentum Melemah: SMA 5 berada di bawah SMA 20 (Kondisi Dead Cross aktif).")

    # Analisa Indikator RSI 14
    if current_rsi <= 30:
        score += 20
        reasons.append(f"Peluang Rebound (Oversold): RSI {current_rsi:.1f} berada di zona jenuh jual ekstrem. Tekanan jual mereda, potensi pembalikan arah naik sangat tinggi.")
    elif 30 < current_rsi <= 45:
        score += 10
        reasons.append(f"Akumulasi Awal: RSI {current_rsi:.1f} mulai pulih dari zona bawah, mengindikasikan minat beli baru mulai masuk.")
    elif 45 < current_rsi <= 60:
        reasons.append(f"Momentum Netral: RSI {current_rsi:.1f} berada di rentang tengah yang wajar dan terkonsolidasi.")
    elif 60 < current_rsi <= 70:
        score -= 10
        reasons.append(f"Waspada Jenuh Beli: RSI {current_rsi:.1f} mendekati zona tinggi, ruang apresiasi jangka pendek mulai terbatas.")
    else:
        score -= 20
        reasons.append(f"Bahaya Koreksi (Overbought): RSI {current_rsi:.1f} berada di zona jenuh beli ekstrem. Risiko koreksi aksi ambil untung (profit taking) sangat tinggi.")

    # Analisa Bollinger Bands
    latest_bb_lower = bb_lower.iloc[-1]
    latest_bb_upper = bb_upper.iloc[-1]
    if current_price <= latest_bb_lower:
        score += 10
        reasons.append(f"Diskon Harga: Harga menyentuh pita bawah Bollinger Band (Rp {int(latest_bb_lower):,}), titik pantulan beli (Bounce Back).")
    elif current_price >= latest_bb_upper:
        score -= 10
        reasons.append(f"Rentang Tertinggi: Harga menyentuh pita atas Bollinger Band (Rp {int(latest_bb_upper):,}), potensi penolakan harga di resisten.")

    # Analisa Konfirmasi Volume (jika data volume tersedia)
    if len(volumes) >= 5 and volumes.iloc[-1] > 0:
        avg_vol_5 = volumes.rolling(5).mean().iloc[-1]
        if avg_vol_5 > 0 and volumes.iloc[-1] > (avg_vol_5 * 1.25):
            if len(closes) >= 2 and current_price >= closes.iloc[-2]:
                score += 10
                reasons.append(f"Konfirmasi Volume: Volume transaksi ({int(volumes.iloc[-1]):,} lembar) melonjak di atas rata-rata dengan harga menguat (Akumulasi Aktif).")
            elif len(closes) >= 2 and current_price < closes.iloc[-2]:
                score -= 10
                reasons.append(f"Distribusi Volume: Volume transaksi ({int(volumes.iloc[-1]):,} lembar) tinggi saat harga turun (Tekanan Jual Masif).")

    # Batasi skor 0 - 100
    score = int(max(0, min(100, score)))

    # Penentuan Rekomendasi Aksi & Setup Trading
    if score >= 75:
        action = "STRONG BUY"
        action_id = "SANGAT DISARANKAN BELI"
        action_badge = "success"
        action_icon = "bi-arrow-up-circle-fill"
        status_text = "Bullish Kuat"
        strategy_summary = "Kombinasi indikator teknikal sangat positif. Waktu yang sangat tepat untuk membuka posisi beli atau menambah porsi (akumulasi agresif)."
    elif score >= 60:
        action = "BUY"
        action_id = "SINYAL BELI / AKUMULASI"
        action_badge = "primary"
        action_icon = "bi-bag-plus-fill"
        status_text = "Bullish"
        strategy_summary = "Indikator teknikal mengonfirmasi momentum kenaikan. Disarankan masuk bertahap dengan strategi Buy on Weakness."
    elif score >= 40:
        action = "HOLD / WAIT"
        action_id = "TAHAN / WAIT & SEE"
        action_badge = "warning"
        action_icon = "bi-pause-circle-fill"
        status_text = "Konsolidasi"
        strategy_summary = "Harga dalam fase konsolidasi atau sideways. Tahan bagi yang sudah memiliki barang, dan pantau titik konfirmasi sebelum membeli."
    elif score >= 25:
        action = "SELL"
        action_id = "SINYAL JUAL / TAKE PROFIT"
        action_badge = "danger"
        action_icon = "bi-bag-dash-fill"
        status_text = "Bearish"
        strategy_summary = "Momentum harga melemah atau mendekati resisten. Waktu yang baik untuk mengamankan modal dan merealisasikan keuntungan (Profit Taking)."
    else:
        action = "STRONG SELL"
        action_id = "SANGAT DISARANKAN JUAL / CUT LOSS"
        action_badge = "dark"
        action_icon = "bi-arrow-down-circle-fill"
        status_text = "Bearish Kuat"
        strategy_summary = "Tekanan jual sangat dominan. Disiplin batasi risiko dengan Stop Loss / Cut Loss untuk menghindari penurunan lebih dalam."

    # Kalkulasi Target Beli, Take Profit, dan Stop Loss
    P = float(current_price)
    sup = float(support) if support and support > 0 else P * 0.95
    res = float(resistance) if resistance and resistance > 0 else P * 1.05

    # Area Entry Beli
    if score >= 60:
        entry_low = round(max(sup, P * 0.98), 0)
        entry_high = round(P * 1.005, 0)
    elif score >= 40:
        entry_low = round(sup, 0)
        entry_high = round(sup * 1.02, 0)
    else:
        entry_low = round(sup * 0.97, 0)
        entry_high = round(sup, 0)

    # Take Profit 1 & 2
    tp_1 = round(max(P * 1.03, min(res, P * 1.06)), 0)
    tp_2 = round(max(res, P * 1.10), 0)

    # Stop Loss (Proteksi Modal)
    stop_loss = round(min(P * 0.96, sup * 0.98), 0)

    # Risk-Reward Ratio
    potential_gain = max(0.0, tp_1 - P)
    potential_loss = max(1.0, P - stop_loss)
    rr_ratio = round(potential_gain / potential_loss, 1)

    recommendation = {
        'action': action,
        'action_id': action_id,
        'badge': action_badge,
        'icon': action_icon,
        'score': score,
        'status': status_text,
        'entry_range': f"Rp {int(entry_low):,} - Rp {int(entry_high):,}",
        'entry_low': int(entry_low),
        'entry_high': int(entry_high),
        'tp1': int(tp_1),
        'tp1_pct': round(((tp_1 - P) / P) * 100, 1) if P else 0,
        'tp2': int(tp_2),
        'tp2_pct': round(((tp_2 - P) / P) * 100, 1) if P else 0,
        'stop_loss': int(stop_loss),
        'sl_pct': round(((stop_loss - P) / P) * 100, 1) if P else 0,
        'risk_reward': f"1 : {max(1.0, rr_ratio):.1f}",
        'reasons': reasons,
        'strategy': strategy_summary,
    }

    return {
        'sma_5': [round(x, 2) for x in sma_5_series.tolist()],
        'sma_20': [round(x, 2) for x in sma_20_series.tolist()],
        'ema_9': [round(x, 2) for x in ema_9_series.tolist()],
        'bb_upper': [round(x, 2) for x in bb_upper.tolist()],
        'bb_lower': [round(x, 2) for x in bb_lower.tolist()],
        'rsi': current_rsi,
        'rsi_signal': rsi_signal,
        'rsi_badge': rsi_badge,
        'trend_signal': trend_signal,
        'trend_badge': trend_badge,
        'support': support,
        'resistance': resistance,
        'score': score,
        'reasons': reasons,
        'recommendation': recommendation,
    }
