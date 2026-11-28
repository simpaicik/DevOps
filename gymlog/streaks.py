"""Seri (streak) ve coin ödülü hesapları.

Seri: antrenman kaydı olan ardışık takvim günleri. Bugün henüz antrenman
yapılmadıysa dünkü seri hâlâ "canlı" sayılır; bugün kayıt girilirse devam eder,
bir gün boş geçerse sıfırlanır.

Coin: antrenman yapılan her gün bir kez günlük ödül verilir. Ödül seri uzadıkça
haftadan haftaya artar: ilk hafta (1–7. gün) 10 coin, ikinci hafta 15, üçüncü
hafta 20 ... en fazla 50 coin.
"""
from datetime import date, timedelta

BASE_REWARD = 10      # serinin ilk haftasında günlük coin
WEEKLY_BONUS = 5      # her tamamlanan seri haftası için günlük ödüle eklenen
MAX_REWARD = 50       # günlük ödülün üst sınırı


def daily_reward(streak):
    """Seri uzunluğu `streak` olan gün için verilecek coin."""
    if streak < 1:
        return 0
    return min(BASE_REWARD + WEEKLY_BONUS * ((streak - 1) // 7), MAX_REWARD)


def _as_dates(days):
    return {d if isinstance(d, date) else date.fromisoformat(d) for d in days}


def streak_ending(days, day):
    """`day` gününde biten ardışık antrenman günü sayısı (o gün yoksa 0)."""
    days = _as_dates(days)
    day = day if isinstance(day, date) else date.fromisoformat(day)
    n = 0
    while day - timedelta(days=n) in days:
        n += 1
    return n


def current_streak(days, today):
    """Bugün ya da dün biten seri; ikisi de boşsa 0."""
    today = today if isinstance(today, date) else date.fromisoformat(today)
    return streak_ending(days, today) or streak_ending(days, today - timedelta(days=1))


def best_streak(days):
    """Tüm zamanların en uzun serisi."""
    days = _as_dates(days)
    best = 0
    for d in days:
        if d - timedelta(days=1) not in days:  # yalnızca seri başlangıçlarından say
            n = 1
            while d + timedelta(days=n) in days:
                n += 1
            best = max(best, n)
    return best


def streak_status(days, today):
    """Ana sayfadaki seri kartı için özet.

    `today_streak`: bugün antrenman yapılırsa (ya da yapıldıysa) serinin uzunluğu;
    `today_reward` bu güne ait ödüldür. `days_to_raise` gün sonra günlük ödül
    `next_reward` olur (ödül üst sınırdaysa None).
    """
    today = today if isinstance(today, date) else date.fromisoformat(today)
    days = _as_dates(days)
    trained_today = today in days
    streak = current_streak(days, today)
    today_streak = streak if trained_today else streak + 1
    reward = daily_reward(today_streak)
    days_to_raise = next_reward = None
    if reward < MAX_REWARD:
        days_to_raise = 7 - (today_streak - 1) % 7
        next_reward = daily_reward(today_streak + days_to_raise)
    return {
        "streak": streak,
        "best": best_streak(days),
        "trained_today": trained_today,
        "today_streak": today_streak,
        "today_reward": reward,
        "days_to_raise": days_to_raise,
        "next_reward": next_reward,
        # Son 7 gün (eskiden yeniye): (tarih, antrenman var mı)
        "week": [(today - timedelta(days=i), today - timedelta(days=i) in days)
                 for i in range(6, -1, -1)],
    }
