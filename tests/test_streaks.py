"""Seri (streak) ve coin sistemi."""
from datetime import date, timedelta

from gymlog import coins
from gymlog.db import get_db
from gymlog.streaks import best_streak, current_streak, daily_reward, streak_ending, streak_status

TODAY = date.today()


def ago(n):
    return (TODAY - timedelta(days=n)).isoformat()


def log(client, day, exercise="Bench Press"):
    return client.post("/workouts", data={
        "date": day, "exercise": exercise, "equipment": "Barbell",
        "sets": "3", "reps": "8", "weight_kg": "60",
    }, follow_redirects=True)


# --- Saf hesaplar ---------------------------------------------------------

def test_reward_grows_week_by_week_and_is_capped():
    assert [daily_reward(n) for n in (1, 7, 8, 14, 15, 22)] == [10, 10, 15, 15, 20, 25]
    assert daily_reward(57) == 50 and daily_reward(365) == 50
    assert daily_reward(0) == 0


def test_streak_counts_consecutive_days_only():
    days = ["2026-11-01", "2026-11-02", "2026-11-03", "2026-11-05"]
    assert streak_ending(days, "2026-11-03") == 3
    assert streak_ending(days, "2026-11-05") == 1
    assert streak_ending(days, "2026-11-04") == 0
    assert best_streak(days) == 3


def test_current_streak_survives_until_end_of_today():
    days = ["2026-11-10", "2026-11-11"]
    assert current_streak(days, "2026-11-11") == 2   # bugün yapıldı
    assert current_streak(days, "2026-11-12") == 2   # bugün henüz yapılmadı, dün yapıldı
    assert current_streak(days, "2026-11-13") == 0   # bir gün boş geçti


def test_status_tells_next_reward_raise():
    # 6 günlük seri, bugün henüz yok: bugün 7. gün (10 coin), yarın 8. gün (15 coin)
    days = [(date(2026, 11, 20) - timedelta(days=i)).isoformat() for i in range(1, 7)]
    s = streak_status(days, date(2026, 11, 20))
    assert (s["streak"], s["trained_today"], s["today_reward"]) == (6, False, 10)
    assert (s["days_to_raise"], s["next_reward"]) == (1, 15)
    assert [done for _, done in s["week"]] == [True] * 6 + [False]


# --- Uygulama üzerinden ---------------------------------------------------

def test_first_workout_of_today_gives_coins_once(client, app):
    html = log(client, TODAY.isoformat()).data.decode()
    assert "+10 coin! 1 günlük seri" in html
    html = log(client, TODAY.isoformat(), "Squat").data.decode()
    assert "coin!" not in html  # aynı gün ikinci kayıt ödül vermez
    with app.app_context():
        assert coins.balance(get_db()) == 10


def test_streak_increases_reward(client, app):
    for n in range(7, 0, -1):     # geçmiş 7 gün: seri oluşur ama coin vermez
        log(client, ago(n))
    with app.app_context():
        assert coins.balance(get_db()) == 0
    html = log(client, TODAY.isoformat()).data.decode()
    assert "+15 coin! 8 günlük seri" in html
    page = client.get("/").data.decode()
    card = page[page.index('id="streak"'):page.index('id="template-quick"')]
    assert '8 <small>gün</small>' in card
    assert 'id="coin-balance"' in card and "</span>15</div>" in card
    assert "Bugünün ödülü alındı (+15)" in card


def test_backdated_workout_does_not_give_coins(client, app):
    html = log(client, ago(3)).data.decode()
    assert "coin!" not in html
    with app.app_context():
        assert coins.balance(get_db()) == 0


def test_deleting_and_relogging_today_does_not_double_award(client, app):
    log(client, TODAY.isoformat())
    with app.app_context():
        wid = get_db().execute("SELECT id FROM workouts").fetchone()[0]
    client.post(f"/workouts/{wid}/delete")
    html = log(client, TODAY.isoformat()).data.decode()
    assert "coin!" not in html
    with app.app_context():
        assert coins.balance(get_db()) == 10


def test_template_apply_also_awards_coins(client):
    client.post("/templates", data={"name": "Push", "exercise": "Bench Press",
                                    "equipment": "Barbell", "sets": "3", "reps": "8",
                                    "weight_kg": "60"})
    html = client.post("/templates/1/apply", follow_redirects=True).data.decode()
    assert "+10 coin!" in html


def test_empty_state_shows_todays_potential_reward(client):
    card = client.get("/").data.decode()
    card = card[card.index('id="streak"'):card.index('id="template-quick"')]
    assert '0 <small>gün</small>' in card
    assert "+10 coin" in card


def test_spend_is_ready_for_future_shop(app):
    with app.app_context():
        db = get_db()
        assert coins.spend(db, 5, "shop:test") is False   # bakiye yok
        db.execute("INSERT INTO coin_transactions (day, amount, reason) VALUES ('2026-11-01', 30, 'daily')")
        assert coins.spend(db, 20, "shop:frame") is True
        assert coins.balance(db) == 10
        assert coins.spend(db, 20, "shop:frame") is False
