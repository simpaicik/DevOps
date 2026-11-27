"""Hareket bazlı gelişim grafiği (#4) kabul kriterleri."""
from gymlog.progress import build_chart, progress_series, y_scale

VALID = {"date": "2026-11-20", "exercise": "Bench Press", "equipment": "Barbell",
         "sets": "3", "reps": "10", "weight_kg": "50"}


def W(d, ex, kg, sets=3, reps=10):
    return {"date": d, "exercise": ex, "weight_kg": kg, "sets": sets, "reps": reps}


def test_series_groups_by_day_oldest_first():
    rows = [W("2026-11-08", "Bench", 85), W("2026-11-01", "Bench", 80),
            W("2026-11-08", "Bench", 70, sets=2), W("2026-11-02", "Squat", 100)]
    s = progress_series(rows, "Bench")
    assert [p["date"] for p in s] == ["2026-11-01", "2026-11-08"]
    assert s[1]["max_weight"] == 85
    assert s[1]["volume"] == 3 * 10 * 85 + 2 * 10 * 70
    assert s[1]["sets"] == 5


def test_series_name_match_ignores_case_and_spaces():
    rows = [W("2026-11-01", "Bench Press", 80), W("2026-11-02", " bench press ", 82.5)]
    assert len(progress_series(rows, "BENCH PRESS")) == 2


def test_unknown_exercise_gives_empty_series():
    assert progress_series([W("2026-11-01", "Bench", 80)], "Deadlift") == []
    assert build_chart([], "max_weight") is None


def test_chart_points_rise_with_weight():
    s = progress_series([W("2026-11-01", "B", 80), W("2026-11-08", "B", 85),
                         W("2026-11-15", "B", 90)], "B")
    c = build_chart(s, "max_weight")
    xs = [p["x"] for p in c["points"]]
    ys = [p["y"] for p in c["points"]]
    assert xs == sorted(xs)
    assert ys[0] > ys[1] > ys[2]          # SVG'de yukarı = küçük y
    assert c["ticks"][0]["value"] <= 80 and c["ticks"][-1]["value"] >= 90


def test_single_point_and_flat_values_do_not_crash():
    c = build_chart([{"date": "2026-11-01", "max_weight": 60, "volume": 1800}], "max_weight")
    assert len(c["points"]) == 1
    lo, hi, step = y_scale([60, 60])
    assert lo < 60 < hi and step > 0


def test_three_days_render_three_points(client):
    for d, kg in [("2026-11-01", "80"), ("2026-11-08", "85"), ("2026-11-15", "90")]:
        client.post("/workouts", data=dict(VALID, date=d, weight_kg=kg))
    html = client.get("/progress?exercise=Bench Press").data.decode()
    weight = html[html.index('id="weight-chart"'):html.index('id="volume-chart"')]
    assert weight.count('class="point"') == 3
    assert "2026-11-15: 90 kg" in weight
    assert 'id="progress-table"' in html


def test_exercise_without_data_shows_no_data(client):
    client.post("/workouts", data=VALID)
    html = client.get("/progress?exercise=Deadlift").data.decode()
    assert "Veri yok" in html
    assert 'class="point"' not in html


def test_progress_page_without_any_workouts(client):
    resp = client.get("/progress")
    assert resp.status_code == 200
    assert "Veri yok" in resp.data.decode()


def test_default_selection_is_most_logged_exercise(client):
    client.post("/workouts", data=dict(VALID, exercise="Squat"))
    client.post("/workouts", data=dict(VALID, date="2026-11-01"))
    client.post("/workouts", data=dict(VALID, date="2026-11-02"))
    html = client.get("/progress").data.decode()
    assert "<option selected>Bench Press</option>" in html
