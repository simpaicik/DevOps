"""Antrenman şablonları: form doğrulama ve şablondan bugünün setlerini üretme."""

OPTIONAL_NUMBERS = [
    ("sets", "Set", int, 1),
    ("reps", "Tekrar", int, 1),
    ("weight_kg", "Ağırlık", float, 0),
]
ITEM_FIELDS = ["exercise", "equipment"] + [f for f, *_ in OPTIONAL_NUMBERS]


def form_rows(form):
    """Formdaki paralel listeleri (exercise[], equipment[], ...) satırlara çevirir.
    Hareket adı boş olan satırlar atlanır."""
    columns = {f: form.getlist(f) for f in ITEM_FIELDS}
    count = max((len(v) for v in columns.values()), default=0)
    rows = []
    for i in range(count):
        row = {f: (columns[f][i] if i < len(columns[f]) else "").strip() for f in ITEM_FIELDS}
        if row["exercise"]:
            rows.append(row)
    return rows


def validate_template(form, existing_names):
    """Şablon formunu doğrular. (ad, satırlar, hatalar) döndürür.
    Set, tekrar ve ağırlık boş bırakılabilir (None olarak saklanır)."""
    errors = []
    name = form.get("name", "").strip()
    if not name:
        errors.append("Şablon adı boş olamaz.")
    elif name.casefold() in {n.casefold() for n in existing_names}:
        errors.append(f"\"{name}\" adında bir şablon zaten var.")

    rows = form_rows(form)
    if not rows:
        errors.append("Şablona en az bir hareket ekleyin.")
    items = []
    for n, row in enumerate(rows, start=1):
        item = {"exercise": row["exercise"], "equipment": row["equipment"]}
        if not row["equipment"]:
            errors.append(f"{n}. satır ({row['exercise']}): ekipman boş olamaz.")
        for field, label, cast, minimum in OPTIONAL_NUMBERS:
            raw = row[field].replace(",", ".")
            if raw == "":
                item[field] = None
                continue
            try:
                value = cast(raw)
            except ValueError:
                errors.append(f"{n}. satır ({row['exercise']}): {label} geçerli bir sayı olmalı.")
                continue
            if value < minimum:
                errors.append(f"{n}. satır ({row['exercise']}): {label} en az {minimum} olmalı.")
            item[field] = value
        items.append(item)
    return name, items, errors


def is_complete(item):
    """Set, tekrar ve ağırlığı dolu satır doğrudan kayda dönüştürülebilir."""
    return all(item[f] is not None for f, *_ in OPTIONAL_NUMBERS)


def workouts_for_day(items, day):
    """Tüm satırları dolu bir şablondan o günün kayıtlarını üretir."""
    return [
        {"date": day, "exercise": i["exercise"], "equipment": i["equipment"],
         "sets": i["sets"], "reps": i["reps"], "weight_kg": i["weight_kg"]}
        for i in items
    ]
