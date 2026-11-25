from gymlog import create_app

VALID = {
    "date": "2026-11-20", "exercise": "Bench Press", "equipment": "Barbell",
    "sets": "3", "reps": "10", "weight_kg": "50",
}


def test_add_workout_appears_in_list(client):
    resp = client.post("/workouts", data=VALID, follow_redirects=True)
    assert resp.status_code == 200
    html = resp.data.decode()
    assert "Bench Press" in html
    assert "Barbell" in html
    assert "kaydı eklendi" in html


def test_workout_persists_across_app_restart(tmp_path):
    db_path = str(tmp_path / "persist.db")
    app1 = create_app({"TESTING": True, "DATABASE": db_path})
    app1.test_client().post("/workouts", data=VALID)

    app2 = create_app({"TESTING": True, "DATABASE": db_path})
    assert "Bench Press" in app2.test_client().get("/").data.decode()


def test_invalid_input_is_rejected(client):
    bad = dict(VALID, sets="0", weight_kg="-5", exercise="")
    resp = client.post("/workouts", data=bad, follow_redirects=True)
    html = resp.data.decode()
    assert "Set en az 1 olmalı." in html
    assert "Ağırlık en az 0 olmalı." in html
    assert "Hareket boş olamaz." in html
    assert 'id="workouts"' not in html  # tablo oluşmadı = kayıt eklenmedi


def test_non_numeric_input_is_rejected(client):
    resp = client.post("/workouts", data=dict(VALID, reps="on"), follow_redirects=True)
    assert "Tekrar geçerli bir sayı olmalı." in resp.data.decode()


def test_newest_workout_listed_first(client):
    client.post("/workouts", data=dict(VALID, date="2026-11-01", exercise="Squat"))
    client.post("/workouts", data=dict(VALID, date="2026-11-15", exercise="Deadlift"))
    html = client.get("/").data.decode()
    table = html[html.index('id="workouts"'):]
    assert table.index("Deadlift") < table.index("Squat")
