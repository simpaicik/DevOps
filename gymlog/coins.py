"""Coin bakiyesi ve günlük ödül kaydı (veritabanı tarafı).

Bakiye `coin_transactions` tablosundaki tutarların toplamıdır. Market eklendiğinde
harcamalar negatif tutarlı satırlar olarak yazılacak; `spend` şimdiden hazırdır.
"""
from datetime import date

from .streaks import daily_reward, streak_ending


def workout_days(db):
    return [r["date"] for r in db.execute("SELECT DISTINCT date FROM workouts")]


def balance(db):
    return db.execute("SELECT COALESCE(SUM(amount), 0) FROM coin_transactions").fetchone()[0]


def award_daily(db, today=None):
    """Bugün antrenman kaydı varsa ve bugünün ödülü verilmediyse ödülü yazar.

    Yalnızca bugünün tarihi sayılır: geçmiş bir güne sonradan girilen kayıt seriyi
    uzatır ama coin kazandırmaz. Döndürür: (coin, seri) ya da ödül verilmediyse None.
    """
    today = (today or date.today()).isoformat()
    days = workout_days(db)
    if today not in days:
        return None
    if db.execute(
        "SELECT 1 FROM coin_transactions WHERE day = ? AND reason = 'daily'", (today,)
    ).fetchone():
        return None
    streak = streak_ending(days, today)
    amount = daily_reward(streak)
    db.execute(
        "INSERT INTO coin_transactions (day, amount, reason, streak) VALUES (?, ?, 'daily', ?)",
        (today, amount, streak),
    )
    db.commit()
    return amount, streak


def spend(db, amount, reason, today=None):
    """İleride market için: bakiye yetiyorsa harcamayı yazar, True döndürür."""
    if amount <= 0 or balance(db) < amount:
        return False
    db.execute(
        "INSERT INTO coin_transactions (day, amount, reason) VALUES (?, ?, ?)",
        ((today or date.today()).isoformat(), -amount, reason),
    )
    db.commit()
    return True


def recent(db, limit=7):
    return db.execute(
        "SELECT * FROM coin_transactions ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
