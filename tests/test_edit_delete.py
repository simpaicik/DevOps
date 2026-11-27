"""Kayıt düzenleme ve silme (#6) kabul kriterleri."""

VALID = {
    "date": "2026-11-20", "exercise": "Bench Press", "equipment": "Barbell",
    "sets": "3", "reps": "10", "weight_kg": "50",
}


def daily_total(html, day):
    table = html[html.index('id="daily-totals"'):]
    row = table[table.index(day):]
    return row[row.index('class="num">') + len('class="num">'):row.index("</td></tr>")]


def test_deleted_workout_leaves_list_and_daily_total(client):
    client.post("/workouts", data=VALID)                                   # 1500
    client.post("/workouts", data=dict(VALID, exercise="Barbell Row", sets="2"))  # 1000
    assert daily_total(client.get("/").data.decode(), "2026-11-20") == "2500"

    resp = client.post("/workouts/2/delete", follow_redirects=True)
    html = resp.data.decode()
    assert "kaydı silindi" in html
    table = html[html.index('id="workouts"'):html.index('id="daily-totals"')]
    assert "Barbell Row" not in table
    assert daily_total(html, "2026-11-20") == "1500"


def test_deleting_last_workout_shows_empty_state(client):
    client.post("/workouts", data=VALID)
    html = client.post("/workouts/1/delete", follow_redirects=True).data.decode()
    assert "Henüz kayıt yok" in html


def test_edit_form_is_prefilled(client):
    client.post("/workouts", data=dict(VALID, weight_kg="52.5"))
    html = client.get("/workouts/1/edit").data.decode()
    assert 'value="Bench Press"' in html
    assert 'value="52.5"' in html
    assert 'value="2026-11-20"' in html


def test_edited_values_appear_in_list_and_volume(client):
    client.post("/workouts", data=VALID)  # 3×10×50 = 1500
    resp = client.post("/workouts/1/edit", follow_redirects=True,
                       data=dict(VALID, exercise="Incline Bench Press", sets="4", reps="8", weight_kg="60"))
    html = resp.data.decode()
    assert "kaydı güncellendi" in html
    table = html[html.index('id="workouts"'):html.index('id="daily-totals"')]
    assert "Incline Bench Press" in table
    assert ">1920<" in table            # 4×8×60
    assert ">1500<" not in table
    assert daily_total(html, "2026-11-20") == "1920"


def test_invalid_edit_is_rejected_and_keeps_old_values(client):
    client.post("/workouts", data=VALID)
    resp = client.post("/workouts/1/edit", follow_redirects=True, data=dict(VALID, sets="0"))
    html = resp.data.decode()
    assert "Set en az 1 olmalı." in html
    assert "Kaydı düzenle" in html  # form sayfasında kaldı
    assert ">1500<" in client.get("/").data.decode()


def test_edit_updates_personal_records(client):
    client.post("/workouts", data=dict(VALID, date="2026-11-01", weight_kg="80"))
    client.post("/workouts", data=dict(VALID, date="2026-11-08", weight_kg="85"))
    assert client.get("/").data.decode().count('class="badge-pr"') == 1
    client.post("/workouts/2/edit", data=dict(VALID, date="2026-11-08", weight_kg="75"))
    assert 'class="badge-pr"' not in client.get("/").data.decode()


def test_unknown_workout_returns_404(client):
    assert client.get("/workouts/99/edit").status_code == 404
    assert client.post("/workouts/99/edit", data=VALID).status_code == 404
    assert client.post("/workouts/99/delete").status_code == 404


def test_delete_requires_post(client):
    client.post("/workouts", data=VALID)
    assert client.get("/workouts/1/delete").status_code == 405
