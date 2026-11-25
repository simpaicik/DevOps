# GymLog: Antrenman Hacmi ve Gelişim Takipçisi

## Problem ve hedef kullanıcı
Düzenli spor salonuna giden kişiler, hangi makine veya ekipmanla hangi hareketi kaç set,
kaç tekrar ve kaç kilo yaptıklarını genellikle not defterinde ya da dağınık telefon
notlarında tutar. Bu yüzden zaman içinde gerçekten ilerleyip ilerlemediklerini görmek zordur.

**GymLog**, bu kişilerin (başlangıç ve orta seviye sporcular) antrenmanlarını tek bir yerde
kaydetmesini, her kaydın **antrenman hacmini** (set × tekrar × kg) görmesini ve gelişimini
takip etmesini sağlayan basit bir web uygulamasıdır.

## Pano (board)
- GitHub Projects panosu: **<PANO_BAĞLANTISI_BURAYA>**
- Kart metinleri: [`docs/BOARD.md`](docs/BOARD.md)

## Teknolojiler
Python 3.10+, Flask, SQLite, pytest, GitHub Actions (CI)

## Çalıştırma
```bash
git clone <DEPO_BAĞLANTISI>
cd <depo-klasörü>
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
flask --app gymlog run              # http://127.0.0.1:5000
```
Veritabanı (`instance/gymlog.db`) ilk çalıştırmada otomatik oluşturulur.
Sıfırlamak için dosyayı silebilir ya da `flask --app gymlog init-db` çalıştırabilirsiniz.

## Testler
```bash
pytest -v
```
Her push'ta ve pull request'te GitHub Actions testleri otomatik çalıştırır (`.github/workflows/ci.yml`).

## Özellikleri deneme

### Özellik 1: Antrenman kaydı ekleme ve listeleme
1. Uygulamayı çalıştırıp `http://127.0.0.1:5000` adresini açın.
2. Formu doldurun, örneğin: Hareket `Bench Press`, Ekipman `Barbell`, Set `3`, Tekrar `10`, Kg `50`. Ardından **Kaydet**'e basın.
3. Kayıt "Kayıtlar" tablosunda görünür. Sayfayı yenileyin ya da uygulamayı yeniden başlatın: kayıt yerinde durur.
4. Set alanına `0` ya da Kg alanına negatif bir değer girip gönderin. Kayıt eklenmez ve hata mesajı gösterilir.

### Özellik 2: Antrenman hacmi hesaplama
1. Yukarıdaki kaydın **Hacim (kg)** sütununda `1500` (3 × 10 × 50) yazar.
2. Aynı tarihe ikinci bir kayıt ekleyin, örneğin `Barbell Row`, 2 set × 10 tekrar × 50 kg (hacim 1000).
3. **Günlük toplam hacim** tablosunda o gün için `2500` görünür. **Hareket bazında toplam hacim** tablosu her hareketin toplamını büyükten küçüğe listeler.

Her iki özellik için otomatik testler: `tests/test_workouts.py`, `tests/test_volume.py`.
