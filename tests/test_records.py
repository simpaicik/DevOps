from gymlog.records import best_lifts, personal_record_ids

VALID = {"date": "2026-11-20", "exercise": "Bench Press", "equipment": "Barbell",
         "sets": "3", "reps": "5"}


def W(id, d, ex, kg):
    return {"id": id, "date": d, "exercise": ex, "weight_kg": kg}


def test_heavier_than_previous_best_is_pr():
    rows = [W(1, "2026-11-01", "Bench", 80), W(2, "2026-11-08", "Bench", 85)]
    assert personal_record_ids(rows) == {2}


def test_equal_or_lower_weight_is_not_pr():
    rows = [W(1, "2026-11-01", "Bench", 80), W(2, "2026-11-08", "Bench", 80),
            W(3, "2026-11-15", "Bench", 75)]
    assert personal_record_ids(rows) == set()


def test_first_entry_is_not_pr_and_exercises_are_independent():
    rows = [W(1, "2026-11-01", "Bench", 80), W(2, "2026-11-02", "Squat", 60),
            W(3, "2026-11-03", "Squat", 70)]
    assert personal_record_ids(rows) == {3}


def test_chronological_order_not_insert_order():
    # 85 kg'lık kayıt önce girilmiş ama tarihi daha yeni: yine de PR odur.
    rows = [W(1, "2026-11-08", "Bench", 85), W(2, "2026-11-01", "Bench", 80)]
    assert personal_record_ids(rows) == {1}


def test_exercise_name_match_ignores_case_and_spaces():
    rows = [W(1, "2026-11-01", "Bench Press", 80), W(2, "2026-11-02", " bench press", 82.5)]
    assert personal_record_ids(rows) == {2}


def test_best_lifts_sorted_desc():
    rows = [W(1, "2026-11-01", "Bench", 80), W(2, "2026-11-02", "Squat", 100),
            W(3, "2026-11-03", "Bench", 85)]
    assert list(best_lifts(rows).items()) == [("Squat", 100), ("Bench", 85)]


def test_pr_badge_shown_on_page(client):
    client.post("/workouts", data=dict(VALID, date="2026-11-01", weight_kg="80"))
    client.post("/workouts", data=dict(VALID, date="2026-11-08", weight_kg="85"))
    client.post("/workouts", data=dict(VALID, date="2026-11-15", weight_kg="80"))
    html = client.get("/").data.decode()
    assert html.count('class="badge-pr"') == 1
    table = html[html.index('id="workouts"'):]
    pr_row = table[:table.index('class="badge-pr"')]
    assert "2026-11-08" in pr_row and "2026-11-15" in pr_row  # yeni→eski: 15, 08 (PR), 01
    assert "2026-11-01" not in pr_row


def test_new_pr_flash_message(client):
    client.post("/workouts", data=dict(VALID, weight_kg="80", date="2026-11-01"))
    resp = client.post("/workouts", data=dict(VALID, weight_kg="90"), follow_redirects=True)
    assert "Yeni kişisel rekor" in resp.data.decode()
