"""Kişisel rekor (PR) tespiti.

Bir harekette, o ana kadarki en yüksek ağırlık geçildiğinde kayıt PR sayılır.
Hareketin ilk kaydı karşılaştırılacak bir önceki değer olmadığı için PR sayılmaz.
Eşit ağırlık rekor değildir.
"""


def personal_record_ids(workouts):
    """PR olan kayıtların id'lerini küme olarak döndürür.

    Kayıtlar kronolojik sıraya (tarih, sonra id) göre işlenir; böylece geçmiş
    bir tarihe sonradan eklenen kayıt da doğru değerlendirilir.
    Hareket adları büyük/küçük harf ve baştaki/sondaki boşluk farkı gözetmeden eşleşir.
    """
    best = {}
    pr_ids = set()
    for w in sorted(workouts, key=lambda w: (w["date"], w["id"])):
        key = w["exercise"].strip().casefold()
        if key in best and w["weight_kg"] > best[key]:
            pr_ids.add(w["id"])
        best[key] = max(best.get(key, w["weight_kg"]), w["weight_kg"])
    return pr_ids


def best_lifts(workouts):
    """Her hareket için en yüksek ağırlık: {hareket: kg}, ağırlığa göre büyükten küçüğe."""
    best = {}
    for w in workouts:
        if w["weight_kg"] > best.get(w["exercise"], -1):
            best[w["exercise"]] = w["weight_kg"]
    return dict(sorted(best.items(), key=lambda kv: kv[1], reverse=True))
