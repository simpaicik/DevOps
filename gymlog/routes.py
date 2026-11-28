from datetime import date

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from .db import get_db
from .exercises import EXERCISES_BY_GROUP
from .progress import build_chart, progress_series
from .records import best_lifts, personal_record_ids
from .volume import daily_totals, exercise_totals, workout_volume
from .workout_templates import form_rows, is_complete, validate_template, workouts_for_day

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
        templates=load_templates(db),
    )


@bp.post("/workouts")
def add_workout():
    data, errors = validate_workout(request.form)
    if errors:
        for e in errors:
            flash(e, "error")
        return redirect(url_for("main.index"))

    insert_workouts([data])
    flash(f"{data['exercise']} kaydı eklendi.", "success")
    return redirect(url_for("main.index"))


def insert_workouts(rows):
    """Kayıtları ekler; yeni kişisel rekor olanlar için bildirim gösterir."""
    db = get_db()
    new_ids = {}
    for data in rows:
        cur = db.execute(
            "INSERT INTO workouts (date, exercise, equipment, sets, reps, weight_kg)"
            " VALUES (:date, :exercise, :equipment, :sets, :reps, :weight_kg)",
            data,
        )
        new_ids[cur.lastrowid] = data
    db.commit()
    prs = personal_record_ids(db.execute("SELECT * FROM workouts").fetchall())
    for workout_id, data in new_ids.items():
        if workout_id in prs:
            flash(f"Yeni kişisel rekor! {data['exercise']}: {data['weight_kg']:g} kg", "pr")


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


def load_templates(db):
    """Şablonları hareketleriyle birlikte, ada göre sıralı döndürür."""
    templates = [dict(t, items=[]) for t in db.execute(
        "SELECT * FROM templates ORDER BY name COLLATE NOCASE"
    )]
    by_id = {t["id"]: t for t in templates}
    for item in db.execute("SELECT * FROM template_items ORDER BY template_id, position"):
        by_id[item["template_id"]]["items"].append(dict(item))
    for t in templates:
        t["complete"] = all(is_complete(i) for i in t["items"])
    return templates


def get_template_or_404(template_id):
    db = get_db()
    template = next((t for t in load_templates(db) if t["id"] == template_id), None)
    if template is None:
        abort(404)
    return template


@bp.route("/templates", methods=["GET", "POST"])
def templates():
    """Şablon listesi (GET) ve yeni şablon kaydetme (POST)."""
    db = get_db()
    existing = load_templates(db)
    rows = []
    name = ""
    if request.method == "POST":
        name, items, errors = validate_template(request.form, [t["name"] for t in existing])
        if not errors:
            cur = db.execute("INSERT INTO templates (name) VALUES (?)", (name,))
            db.executemany(
                "INSERT INTO template_items (template_id, position, exercise, equipment, sets, reps, weight_kg)"
                " VALUES (:template_id, :position, :exercise, :equipment, :sets, :reps, :weight_kg)",
                [dict(i, template_id=cur.lastrowid, position=n) for n, i in enumerate(items)],
            )
            db.commit()
            flash(f"\"{name}\" şablonu kaydedildi ({len(items)} hareket).", "success")
            return redirect(url_for("main.templates"))
        for e in errors:
            flash(e, "error")
        rows = form_rows(request.form)
    elif request.args.get("from_date"):
        # Bir günün kayıtlarından şablon taslağı: her hareketin o günkü ilk seti.
        name = request.args.get("name", "")
        seen = set()
        for w in db.execute(
            "SELECT * FROM workouts WHERE date = ? ORDER BY id", (request.args["from_date"],)
        ):
            if w["exercise"] not in seen:
                seen.add(w["exercise"])
                rows.append({"exercise": w["exercise"], "equipment": w["equipment"],
                             "sets": w["sets"], "reps": w["reps"], "weight_kg": "%g" % w["weight_kg"]})
    days = [r["date"] for r in db.execute("SELECT DISTINCT date FROM workouts ORDER BY date DESC LIMIT 30")]
    return render_template(
        "templates.html",
        templates=existing,
        rows=rows + [{}] * max(3, 6 - len(rows)),
        name=name,
        days=days,
        exercises=exercise_options(used_exercises(db)),
        equipment=DEFAULT_EQUIPMENT,
    )


@bp.post("/templates/<int:template_id>/delete")
def delete_template(template_id):
    template = get_template_or_404(template_id)
    db = get_db()
    db.execute("DELETE FROM template_items WHERE template_id = ?", (template_id,))
    db.execute("DELETE FROM templates WHERE id = ?", (template_id,))
    db.commit()
    flash(f"\"{template['name']}\" şablonu silindi. Kayıtlı antrenmanlar etkilenmedi.", "success")
    return redirect(url_for("main.templates"))


@bp.post("/templates/<int:template_id>/apply")
def apply_template(template_id):
    """Tek tıkla yükleme: tüm değerleri dolu şablon bugünün kayıtlarına eklenir,
    eksik değer varsa doldurma sayfası açılır."""
    template = get_template_or_404(template_id)
    if not template["complete"]:
        flash("Bu şablonda set/tekrar/ağırlık eksik; değerleri girip kaydedin.", "info")
        return redirect(url_for("main.start_template", template_id=template_id))
    rows = workouts_for_day(template["items"], date.today().isoformat())
    insert_workouts(rows)
    flash(f"\"{template['name']}\" bugünün antrenmanına yüklendi ({len(rows)} kayıt).", "success")
    return redirect(url_for("main.index"))


@bp.route("/templates/<int:template_id>/start", methods=["GET", "POST"])
def start_template(template_id):
    """Şablonu bugüne yüklemeden önce değerleri gözden geçirip düzenleme sayfası."""
    template = get_template_or_404(template_id)
    day = date.today().isoformat()
    rows = template["items"]
    if request.method == "POST":
        day = request.form.get("date", "").strip()
        rows = form_rows(request.form)
        checked = [validate_workout(dict(r, date=day)) for r in rows]
        errors = [e for _, errs in checked for e in errs]
        if not rows:
            errors.append("Kaydedilecek hareket kalmadı.")
        if not errors:
            insert_workouts([data for data, _ in checked])
            flash(f"\"{template['name']}\" antrenmanı kaydedildi ({len(rows)} kayıt).", "success")
            return redirect(url_for("main.index"))
        for e in dict.fromkeys(errors):
            flash(e, "error")
    return render_template(
        "template_start.html",
        template=template,
        rows=rows,
        day=day,
        exercises=exercise_options(used_exercises(get_db())),
        equipment=DEFAULT_EQUIPMENT,
    )


@bp.route("/health")
def health():
    """CI ve dağıtım kontrolleri için basit sağlık uç noktası."""
    return {"status": "ok"}
