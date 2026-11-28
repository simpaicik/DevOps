"""Antrenman şablonları: kaydetme, listeleme, silme ve bugüne yükleme."""
from datetime import date

from werkzeug.datastructures import MultiDict

from gymlog.workout_templates import validate_template

TODAY = date.today().isoformat()

PUSH = MultiDict([
    ("name", "Push günü"),
    ("exercise", "Bench Press"), ("equipment", "Barbell"),
    ("sets", "3"), ("reps", "8"), ("weight_kg", "60"),
    ("exercise", "Overhead Press"), ("equipment", "Barbell"),
    ("sets", "3"), ("reps", "10"), ("weight_kg", "40"),
    ("exercise", ""), ("equipment", ""), ("sets", ""), ("reps", ""), ("weight_kg", ""),
])

LEGS_PARTIAL = MultiDict([
    ("name", "Bacak günü"),
    ("exercise", "Back Squat"), ("equipment", "Barbell"),
    ("sets", "4"), ("reps", ""), ("weight_kg", ""),
])


def workouts_table(html):
    return html[html.index('id="workouts"'):html.index('id="daily-totals"')]


def test_template_is_saved_and_listed(client):
    resp = client.post("/templates", data=PUSH, follow_redirects=True)
    html = resp.data.decode()
    assert "şablonu kaydedildi (2 hareket)" in html
    listing = html[html.index('id="template-list"'):]
    assert "Push günü" in listing
    assert "Bench Press" in listing and "Overhead Press" in listing
    # Ana sayfadaki hızlı başlatma düğmesinde de görünür
    assert "Push günü" in client.get("/").data.decode()


def test_one_click_load_adds_todays_workouts(client):
    client.post("/templates", data=PUSH)
    html = client.post("/templates/1/apply", follow_redirects=True).data.decode()
    assert "bugünün antrenmanına yüklendi (2 kayıt)" in html
    table = workouts_table(html)
    assert table.count(f"<td>{TODAY}</td>") == 2
    assert ">1440<" in table  # 3×8×60
    assert ">1200<" in table  # 3×10×40


def test_template_values_are_optional(client):
    resp = client.post("/templates", data=LEGS_PARTIAL, follow_redirects=True)
    assert "şablonu kaydedildi" in resp.data.decode()
    html = client.get("/templates").data.decode()
    assert "4 × – × – kg" in html


def test_incomplete_template_asks_for_values_before_saving(client):
    client.post("/templates", data=LEGS_PARTIAL)
    resp = client.post("/templates/1/apply")
    assert resp.status_code == 302 and resp.headers["Location"].endswith("/templates/1/start")
    assert "Henüz kayıt yok" in client.get("/").data.decode()

    page = client.get("/templates/1/start").data.decode()
    assert 'value="Back Squat"' in page and f'value="{TODAY}"' in page

    resp = client.post("/templates/1/start", follow_redirects=True, data=MultiDict([
        ("date", TODAY), ("exercise", "Back Squat"), ("equipment", "Barbell"),
        ("sets", "4"), ("reps", "5"), ("weight_kg", "100"),
    ]))
    html = resp.data.decode()
    assert "antrenmanı kaydedildi (1 kayıt)" in html
    assert ">2000<" in workouts_table(html)


def test_start_rejects_missing_values_and_skips_cleared_rows(client):
    client.post("/templates", data=PUSH)
    # Eksik ağırlık: hiçbir şey kaydedilmez
    html = client.post("/templates/1/start", follow_redirects=True, data=MultiDict([
        ("date", TODAY), ("exercise", "Bench Press"), ("equipment", "Barbell"),
        ("sets", "3"), ("reps", "8"), ("weight_kg", ""),
    ])).data.decode()
    assert "Ağırlık geçerli bir sayı olmalı." in html
    assert "Henüz kayıt yok" in client.get("/").data.decode()
    # İkinci satır temizlendi: yalnızca ilki kaydedilir
    html = client.post("/templates/1/start", follow_redirects=True, data=MultiDict([
        ("date", TODAY), ("exercise", "Bench Press"), ("equipment", "Barbell"),
        ("sets", "3"), ("reps", "8"), ("weight_kg", "60"),
        ("exercise", ""), ("equipment", ""), ("sets", ""), ("reps", ""), ("weight_kg", ""),
    ])).data.decode()
    table = workouts_table(html)
    assert "Bench Press" in table and "Overhead Press" not in table


def test_loading_template_flags_personal_record(client):
    client.post("/workouts", data={"date": "2026-11-01", "exercise": "Bench Press",
                                   "equipment": "Barbell", "sets": "3", "reps": "8", "weight_kg": "55"})
    client.post("/templates", data=PUSH)
    html = client.post("/templates/1/apply", follow_redirects=True).data.decode()
    assert "Yeni kişisel rekor! Bench Press: 60 kg" in html


def test_delete_template_keeps_workouts(client):
    client.post("/templates", data=PUSH)
    client.post("/templates/1/apply")
    html = client.post("/templates/1/delete", follow_redirects=True).data.decode()
    assert "şablonu silindi" in html
    assert "Henüz şablon yok" in html
    assert "Bench Press" in workouts_table(client.get("/").data.decode())


def test_unknown_template_returns_404(client):
    assert client.post("/templates/9/apply").status_code == 404
    assert client.get("/templates/9/start").status_code == 404
    assert client.post("/templates/9/delete").status_code == 404


def test_prefill_from_a_days_workouts(client):
    for ex, kg in [("Bench Press", "60"), ("Bench Press", "62.5"), ("Dumbbell Fly", "14")]:
        client.post("/workouts", data={"date": "2026-11-20", "exercise": ex,
                                       "equipment": "Dumbbell", "sets": "3", "reps": "10", "weight_kg": kg})
    html = client.get("/templates?from_date=2026-11-20").data.decode()
    form = html[html.index("Yeni şablon"):]
    assert form.count('placeholder="Hareket" value="Bench Press"') == 1  # hareket başına bir satır
    assert 'value="Dumbbell Fly"' in form and 'value="60"' in form


def test_validation_rules():
    _, _, errors = validate_template(MultiDict([("name", "")]), [])
    assert "Şablon adı boş olamaz." in errors
    assert "Şablona en az bir hareket ekleyin." in errors

    _, _, errors = validate_template(MultiDict([("name", "push GÜNÜ"), ("exercise", "Dip")]), ["Push günü"])
    assert any("zaten var" in e for e in errors)
    assert any("ekipman boş olamaz" in e for e in errors)

    name, items, errors = validate_template(MultiDict([
        ("name", " Pull "), ("exercise", "Pull-Up"), ("equipment", "Vücut Ağırlığı"),
        ("sets", "0"), ("reps", "x"), ("weight_kg", "0"),
    ]), [])
    assert name == "Pull"
    assert any("Set en az 1" in e for e in errors)
    assert any("Tekrar geçerli bir sayı" in e for e in errors)
    assert items[0]["weight_kg"] == 0
