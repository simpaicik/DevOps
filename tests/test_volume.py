from gymlog.volume import daily_totals, exercise_totals, workout_volume

W = lambda d, ex, s, r, kg: {"date": d, "exercise": ex, "sets": s, "reps": r, "weight_kg": kg}


def test_workout_volume():
    assert workout_volume(3, 10, 50) == 1500
    assert workout_volume(4, 8, 22.5) == 720
    assert workout_volume(3, 12, 0) == 0  # vücut ağırlığı


def test_daily_totals_sum_same_day():
    rows = [W("2026-11-20", "Bench", 3, 10, 50), W("2026-11-20", "Row", 2, 10, 50),
            W("2026-11-19", "Squat", 5, 5, 100)]
    assert daily_totals(rows) == {"2026-11-20": 2500, "2026-11-19": 2500}


def test_exercise_totals_sorted_desc():
    rows = [W("2026-11-20", "Bench", 3, 10, 50), W("2026-11-21", "Bench", 3, 10, 50),
            W("2026-11-21", "Curl", 3, 10, 10)]
    assert list(exercise_totals(rows).items()) == [("Bench", 3000), ("Curl", 300)]


def test_volume_and_daily_total_shown_on_page(client):
    base = {"date": "2026-11-20", "equipment": "Barbell", "sets": "3", "reps": "10"}
    client.post("/workouts", data=dict(base, exercise="Bench Press", weight_kg="50"))  # 1500
    client.post("/workouts", data=dict(base, exercise="Barbell Row", weight_kg="33.5", sets="2", reps="15"))  # 1005
    html = client.get("/").data.decode()
    assert '<td class="num volume">1500</td>' in html
    assert '<td class="num volume">1005</td>' in html
    daily = html[html.index('id="daily-totals"'):]
    assert "<td>2026-11-20</td><td class=\"num\">2505</td>" in daily
