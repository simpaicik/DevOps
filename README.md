# GymLog: Antrenman Hacmi ve Gelişim Takipçisi

## Problem ve hedef kullanıcı
Düzenli spor salonuna giden kişiler, hangi makine veya ekipmanla hangi hareketi kaç set,
kaç tekrar ve kaç kilo yaptıklarını genellikle not defterinde ya da dağınık telefon
notlarında tutar. Bu yüzden zaman içinde gerçekten ilerleyip ilerlemediklerini görmek zordur.

**GymLog**, bu kişilerin (başlangıç ve orta seviye sporcular) antrenmanlarını tek bir yerde
kaydetmesini, her kaydın **antrenman hacmini** (set × tekrar × kg) görmesini ve gelişimini
takip etmesini sağlayan basit bir web uygulamasıdır.

![GymLog ana sayfa](docs/ekran-goruntusu.png)

## Pano (board)
- GitHub Projects panosu: https://github.com/users/simpaicik/projects/1/views/1
- Kart metinleri: [`docs/BOARD.md`](docs/BOARD.md)

## Teknolojiler
Python 3.10+, Flask, SQLite, pytest, Docker (gunicorn), GitHub Actions (CI)

## Çalıştırma
```bash
git clone https://github.com/simpaicik/DevOps.git
cd DevOps
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
flask --app gymlog run              # http://127.0.0.1:5000
```
Veritabanı (`instance/gymlog.db`) ilk çalıştırmada otomatik oluşturulur.
Sıfırlamak için dosyayı silebilir ya da `flask --app gymlog init-db` çalıştırabilirsiniz.

## Docker ile çalıştırma
Bilgisayarda yalnızca [Docker](https://docs.docker.com/get-docker/) kurulu olması yeterlidir; Python kurmanız gerekmez.

```bash
docker compose up --build          # http://127.0.0.1:5000
```
Durdurmak için `Ctrl+C` ya da `docker compose down`. Kayıtlar `gymlog-data` adlı Docker volume'ünde
tutulur; konteyner silinip yeniden oluşturulsa da kaybolmaz (`docker compose down -v` volume'ü de siler).

Compose kullanmadan:
```bash
docker build -t gymlog .
docker run -d --name gymlog -p 5000:5000 -v gymlog-data:/app/instance gymlog
docker ps                           # STATUS sütununda bir süre sonra "(healthy)" görünür
```
İmaj `python:3.12-slim` tabanlıdır, uygulamayı `gunicorn` ile root olmayan bir kullanıcıyla çalıştırır
ve `/health` uç noktasını Docker `HEALTHCHECK` ile yoklar.

## Testler
```bash
pytest -v
```
Her push'ta ve pull request'te GitHub Actions (`.github/workflows/ci.yml`) iki iş çalıştırır:
1. **test**: bağımlılıkları kurar ve `pytest` ile tüm testleri çalıştırır.
2. **docker**: testler geçerse Docker imajını derler, konteyneri başlatır ve `/health` uç noktasının yanıt verdiğini doğrular.

## Özellikleri deneme

### Özellik 1: Antrenman kaydı ekleme ve listeleme
1. Uygulamayı çalıştırıp `http://127.0.0.1:5000` adresini açın.
2. Formu doldurun. **Hareket** alanına tıklayınca kas grubuna göre ayrılmış ~200 hazır hareket önerilir (yazdıkça süzülür); listede olmayan bir hareketi de yazabilirsiniz, sonraki kayıtlarda o da önerilir. Örneğin: Hareket `Bench Press`, Ekipman `Barbell`, Set `3`, Tekrar `10`, Kg `50`. Ardından **Kaydet**'e basın.
3. Kayıt "Kayıtlar" tablosunda görünür. Sayfayı yenileyin ya da uygulamayı yeniden başlatın: kayıt yerinde durur.
4. Set alanına `0` ya da Kg alanına negatif bir değer girip gönderin. Kayıt eklenmez ve hata mesajı gösterilir.

### Özellik 2: Antrenman hacmi hesaplama
1. Yukarıdaki kaydın **Hacim (kg)** sütununda `1500` (3 × 10 × 50) yazar.
2. Aynı tarihe ikinci bir kayıt ekleyin, örneğin `Barbell Row`, 2 set × 10 tekrar × 50 kg (hacim 1000).
3. **Günlük toplam hacim** tablosunda o gün için `2500` görünür. **Hareket bazında toplam hacim** tablosu her hareketin toplamını büyükten küçüğe listeler.

### Özellik 3: Kişisel rekor (PR) tespiti
1. `Bench Press` için `2026-11-01` tarihli, 80 kg'lık bir kayıt ekleyin.
2. Aynı hareket için daha yeni bir tarihte 85 kg'lık kayıt ekleyin. "Yeni kişisel rekor!" mesajı çıkar ve kayıt tabloda turuncu **PR** rozetiyle işaretlenir.
3. Üçüncü bir kayıt olarak 80 kg (ya da 85 kg) girin. Bu kayıt PR sayılmaz, rozet görünmez.
4. **Kişisel rekorlar** tablosunda her hareketin en yüksek ağırlığı listelenir.

Kurallar: hareketin ilk kaydı karşılaştırılacak önceki değer olmadığından PR sayılmaz, eşit ağırlık rekor değildir,
kayıtlar giriş sırasına değil tarihe göre değerlendirilir.

Otomatik testler: `tests/test_workouts.py`, `tests/test_volume.py`, `tests/test_records.py`.
