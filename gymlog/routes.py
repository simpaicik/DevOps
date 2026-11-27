from datetime import date

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from .db import get_db
from .exercises import EXERCISES_BY_GROUP
from .progress import build_chart, progress_series
from .records import best_lifts, personal_record_ids
from .volume import daily_totals, exercise_totals, workout_volume

bp = Blueprint("main", __name__)

DEFAULT_EQUIPMENT = [
    "Barbell", "Dumbbell", "Smith Machine", "Cable", "Leg Press Makinesi",
    "Chest Press Makinesi", "Lat Pulldown Makinesi", "Vücut Ağırlığı",
]


def exercise_options(used):
    """Form önerileri: (hareket, grup) çiftleri. Kullanıcının listede olmayan
    kendi hareketleri en başta, ardından hazır liste kas grubuna göre gelir."""
    known = {name.casefold() for names in EXERCISES_BY_GROUP.values() for name in names}
    options = [(name, "Kendi hareketin") for name in used if name.casefold() not in known]
    for group, names in EXERCISES_BY_GROUP.items():
        options.extend((name, group) for name in names)
    return options


def validate_workout(form):
    """Form verisini doğrular. (temiz_veri, hatalar) döndürür."""
    errors = []
    data = {
        "date": form.get("date", "").strip(),
        "exercise": form.get("exercise", "").strip(),
        "equipment": form.get("equipment", "").strip(),
    }
    for field, label in [("date", "Tarih"), ("exercise", "Hareket"), ("equipment", "Ekipman")]:
        if not data[field]:
            errors.append(f"{label} boş olamaz.")
    if data["date"]:
        try:
            date.fromisoformat(data["date"])
        except ValueError:
            errors.append("Tarih YYYY-AA-GG biçiminde olmalı.")

    for field, label, cast, minimum in [
        ("sets", "Set", int, 1),
        ("reps", "Tekrar", int, 1),
        ("weight_kg", "Ağırlık", float, 0),
    ]:
        raw = form.get(field, "").strip().replace(",", ".")
        try:
            value = cast(raw)
        except ValueError:
            errors.append(f"{label} geçerli bir sayı olmalı.")
            continue
        if value < minimum:
            errors.append(f"{label} en az {minimum} olmalı.")
        data[field] = value
    return data, errors


def used_exercises(db):
    return [r["exercise"] for r in db.execute(
        "SELECT DISTINCT exercise FROM workouts ORDER BY exercise"
    )]


def get_workout_or_404(workout_id):
    row = get_db().execute("SELECT * FROM workouts WHERE id = ?", (workout_id,)).fetchone()
    if row is None:
        abort(404)
    return row


@bp.route("/")
def index():
    db = get_db()
    workouts = db.execute(
        "SELECT * FROM workouts ORDER BY date DESC, id DESC"
    ).fetchall()
    return render_template(
        "index.html",
        workouts=workouts,
        exercises=exercise_options(used_exercises(db)),
        equipment=DEFAULT_EQUIPMENT,
        volume=workout_volume,
        daily=daily_totals(workouts),
        by_exercise=exercise_totals(workouts),
        pr_ids=personal_record_ids(workouts),
        best=best_lifts(workouts),
        today=date.today().isoformat(),
    )


@bp.post("/workouts")
def add_workout():
    data, errors = validate_workout(request.form)
    if errors:
        for e in errors:
            flash(e, "error")
        return redirect(url_for("main.index"))

    db = get_db()
    cur = db.execute(
        "INSERT INTO workouts (date, exercise, equipment, sets, reps, weight_kg)"
        " VALUES (:date, :exercise, :equipment, :sets, :reps, :weight_kg)",
        data,
    )
    db.commit()
    flash(f"{data['exercise']} kaydı eklendi.", "success")
    if cur.lastrowid in personal_record_ids(db.execute("SELECT * FROM workouts").fetchall()):
        flash(f"Yeni kişisel rekor! {data['exercise']}: {data['weight_kg']:g} kg", "pr")
    return redirect(url_for("main.index"))


@bp.route("/workouts/<int:workout_id>/edit", methods=["GET", "POST"])
def edit_workout(workout_id):
    """Kayıtlı bir seti düzenleme formu (GET) ve kaydetme (POST)."""
    workout = get_workout_or_404(workout_id)
    db = get_db()
    if request.method == "POST":
        data, errors = validate_workout(request.form)
        if not errors:
            db.execute(
                "UPDATE workouts SET date = :date, exercise = :exercise, equipment = :equipment,"
                " sets = :sets, reps = :reps, weight_kg = :weight_kg WHERE id = :id",
                dict(data, id=workout_id),
            )
            db.commit()
            flash(f"{data['exercise']} kaydı güncellendi.", "success")
            return redirect(url_for("main.index"))
        for e in errors:
            flash(e, "error")
        workout = dict(workout, **{k: request.form.get(k, "") for k in data})
    return render_template(
        "edit.html",
        workout=workout,
        exercises=exercise_options(used_exercises(db)),
        equipment=DEFAULT_EQUIPMENT,
    )


@bp.post("/workouts/<int:workout_id>/delete")
def delete_workout(workout_id):
    workout = get_workout_or_404(workout_id)
    db = get_db()
    db.execute("DELETE FROM workouts WHERE id = ?", (workout_id,))
    db.commit()
    flash(f"{workout['exercise']} ({workout['date']}) kaydı silindi.", "success")
    return redirect(url_for("main.index"))


@bp.route("/progress")
def progress():
    """Seçilen hareketin zaman içindeki en yüksek ağırlık ve hacim grafiği."""
    db = get_db()
    workouts = db.execute("SELECT * FROM workouts").fetchall()
    # Seçim listesi: en çok kaydı olan hareket en üstte.
    counts = db.execute(
        "SELECT exercise, COUNT(*) AS n FROM workouts GROUP BY exercise ORDER BY n DESC, exercise"
    ).fetchall()
    choices = [r["exercise"] for r in counts]
    selected = request.args.get("exercise", "").strip() or (choices[0] if choices else "")
    series = progress_series(workouts, selected) if selected else []
    return render_template(
        "progress.html",
        choices=choices,
        selected=selected,
        series=series,
        weight_chart=build_chart(series, "max_weight"),
        volume_chart=build_chart(series, "volume"),
    )


@bp.route("/health")
def health():
    """CI ve dağıtım kontrolleri için basit sağlık uç noktası."""
    return {"status": "ok"}
