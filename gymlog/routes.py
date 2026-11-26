from datetime import date

from flask import Blueprint, flash, redirect, render_template, request, url_for

from .db import get_db
from .records import best_lifts, personal_record_ids
from .volume import daily_totals, exercise_totals, workout_volume

bp = Blueprint("main", __name__)

DEFAULT_EQUIPMENT = [
    "Barbell", "Dumbbell", "Smith Machine", "Cable", "Leg Press Makinesi",
    "Chest Press Makinesi", "Lat Pulldown Makinesi", "Vücut Ağırlığı",
]


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


@bp.route("/")
def index():
    db = get_db()
    workouts = db.execute(
        "SELECT * FROM workouts ORDER BY date DESC, id DESC"
    ).fetchall()
    exercises = [r["exercise"] for r in db.execute(
        "SELECT DISTINCT exercise FROM workouts ORDER BY exercise"
    )]
    return render_template(
        "index.html",
        workouts=workouts,
        exercises=exercises,
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


@bp.route("/health")
def health():
    """CI ve dağıtım kontrolleri için basit sağlık uç noktası."""
    return {"status": "ok"}
