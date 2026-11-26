from gymlog.exercises import DEFAULT_EXERCISES, EXERCISES_BY_GROUP

VALID = {"date": "2026-11-20", "equipment": "Barbell", "sets": "3", "reps": "10", "weight_kg": "50"}


def test_default_list_size_and_no_duplicates():
    assert 100 <= len(DEFAULT_EXERCISES) <= 220
    assert len({e.casefold() for e in DEFAULT_EXERCISES}) == len(DEFAULT_EXERCISES)
    assert "Bench Press" in EXERCISES_BY_GROUP["Göğüs"]


def test_form_suggests_default_exercises(client):
    html = client.get("/").data.decode()
    datalist = html[html.index('id="exercise-list"'):html.index("</datalist>")]
    assert '<option value="Bench Press" label="Göğüs">' in datalist
    assert '<option value="Hip Thrust" label="Kalça">' in datalist
    assert datalist.count("<option") == len(DEFAULT_EXERCISES)


def test_custom_exercise_added_to_suggestions_once(client):
    client.post("/workouts", data=dict(VALID, exercise="Salonumdaki Özel Makine"))
    client.post("/workouts", data=dict(VALID, exercise="bench press"))  # listede var, tekrar eklenmez
    html = client.get("/").data.decode()
    datalist = html[html.index('id="exercise-list"'):html.index("</datalist>")]
    assert '<option value="Salonumdaki Özel Makine" label="Kendi hareketin">' in datalist
    assert datalist.count("<option") == len(DEFAULT_EXERCISES) + 1
