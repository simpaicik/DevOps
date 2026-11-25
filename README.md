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
