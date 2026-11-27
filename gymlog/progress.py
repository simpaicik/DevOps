"""Hareket bazlı gelişim grafiği.

Seçilen hareketin kayıtları tarihe göre gruplanır; her gün için en yüksek ağırlık
ve toplam hacim hesaplanır. Grafik, JavaScript ya da dış kütüphane gerektirmeyen
satır içi SVG olarak sunucu tarafında çizilir.
"""
import math

from .volume import workout_volume

# SVG çizim alanı (viewBox birimleri)
WIDTH, HEIGHT = 520, 230
PAD_LEFT, PAD_RIGHT, PAD_TOP, PAD_BOTTOM = 52, 18, 14, 34


def progress_series(workouts, exercise):
    """Hareketin günlük özetini eski→yeni sırayla döndürür.

    Dönüş: [{"date", "max_weight", "volume", "sets"}]. Hareket adı büyük/küçük harf
    ve baştaki/sondaki boşluk farkı gözetmeden eşleşir (PR tespitiyle aynı kural).
    """
    key = exercise.strip().casefold()
    days = {}
    for w in workouts:
        if w["exercise"].strip().casefold() != key:
            continue
        d = days.setdefault(w["date"], {"date": w["date"], "max_weight": 0, "volume": 0, "sets": 0})
        d["max_weight"] = max(d["max_weight"], w["weight_kg"])
        d["volume"] = round(d["volume"] + workout_volume(w["sets"], w["reps"], w["weight_kg"]), 2)
        d["sets"] += w["sets"]
    return [days[k] for k in sorted(days)]


def _nice_step(span, ticks=4):
    raw = span / ticks
    mag = 10 ** math.floor(math.log10(raw))
    for m in (1, 2, 2.5, 5, 10):
        if raw <= m * mag:
            return m * mag
    return 10 * mag


def y_scale(values):
    """Eksen için (alt, üst, adım) üretir: değerleri saran yuvarlak sınırlar."""
    lo, hi = min(values), max(values)
    if lo == hi:
        pad = max(abs(hi) * 0.1, 1)
        lo, hi = lo - pad, hi + pad
    step = _nice_step(hi - lo)
    lo = math.floor(lo / step) * step
    hi = math.ceil(hi / step) * step
    if min(values) >= 0:
        lo = max(lo, 0)
    return lo, hi, step


def build_chart(series, field):
    """Seriden çizime hazır grafik verisi üretir.

    Dönüş: {"points": [{"x","y","date","value"}], "line": "x,y x,y ...",
            "ticks": [{"y","value"}], "labels": [{"x","text"}], "width", "height"}
    """
    if not series:
        return None
    values = [p[field] for p in series]
    lo, hi, step = y_scale(values)
    plot_w = WIDTH - PAD_LEFT - PAD_RIGHT
    plot_h = HEIGHT - PAD_TOP - PAD_BOTTOM

    def sy(v):
        return round(PAD_TOP + plot_h - (v - lo) / (hi - lo) * plot_h, 1)

    n = len(series)
    points = []
    for i, p in enumerate(series):
        x = PAD_LEFT + (plot_w / 2 if n == 1 else plot_w * i / (n - 1))
        points.append({"x": round(x, 1), "y": sy(p[field]), "date": p["date"], "value": p[field]})

    ticks = []
    v = lo
    while v <= hi + step / 1000:
        ticks.append({"y": sy(v), "value": round(v, 2)})
        v += step

    # Çok noktada etiketler üst üste binmesin: en fazla ~6 tarih etiketi.
    every = max(1, math.ceil(n / 6))
    labels = [{"x": pt["x"], "text": pt["date"][5:]}  # AA-GG
              for i, pt in enumerate(points) if i % every == 0 or i == n - 1]
    if n > 1 and len(labels) > 1 and labels[-1]["x"] - labels[-2]["x"] < plot_w / 8:
        labels.pop(-2)

    return {
        "points": points,
        "line": " ".join(f"{p['x']},{p['y']}" for p in points),
        "ticks": ticks,
        "labels": labels,
        "width": WIDTH,
        "height": HEIGHT,
        "left": PAD_LEFT,
        "right": WIDTH - PAD_RIGHT,
        "bottom": HEIGHT - PAD_BOTTOM,
    }
