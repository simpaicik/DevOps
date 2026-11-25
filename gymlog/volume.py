"""Antrenman hacmi hesaplamaları (hacim = set × tekrar × kg)."""
from collections import OrderedDict


def workout_volume(sets, reps, weight_kg):
    return round(sets * reps * weight_kg, 2)


def daily_totals(workouts):
    """Kayıtları tarihe göre gruplar: {tarih: toplam_hacim}, girdi sırasını korur."""
    totals = OrderedDict()
    for w in workouts:
        totals[w["date"]] = totals.get(w["date"], 0) + workout_volume(
            w["sets"], w["reps"], w["weight_kg"]
        )
    return totals


def exercise_totals(workouts):
    """Hareket bazında toplam hacim, büyükten küçüğe sıralı."""
    totals = {}
    for w in workouts:
        totals[w["exercise"]] = totals.get(w["exercise"], 0) + workout_volume(
            w["sets"], w["reps"], w["weight_kg"]
        )
    return dict(sorted(totals.items(), key=lambda kv: kv[1], reverse=True))
