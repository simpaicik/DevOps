# Pano kartları

Bu kartları GitHub Projects panosuna (**Yapılacak / Devam Ediyor / Tamamlandı**)
kopyalayın. En pratik yol, her kartı bir **Issue** olarak açıp projeye eklemektir.
Böylece commit mesajına `#<issue-no>` yazdığınızda bağlantı kartta kendiliğinden görünür.

---

## 1. Antrenman kaydı ekleme ve listeleme
**Açıklama:** Kullanıcı tarih, hareket, ekipman/makine, set, tekrar ve ağırlık (kg)
girerek bir antrenman kaydı oluşturabilir. Kayıtlar ana sayfada yeniden eskiye doğru listelenir.

**Kabul kriterleri:**
- [ ] Form eksiksiz doldurulup gönderildiğinde kayıt tabloda görünür.
- [ ] Sayfa yenilendiğinde ya da uygulama yeniden başlatıldığında kayıt kaybolmaz (SQLite).
- [ ] Set/tekrar 0 veya negatifse, ağırlık negatifse ya da alan boşsa kayıt eklenmez ve hata mesajı gösterilir.

## 2. Antrenman hacmi hesaplama
**Açıklama:** Her kayıt için hacim (set × tekrar × kg) hesaplanır. Ayrıca gün bazında
toplam hacim ve hareket bazında toplam hacim gösterilir.

**Kabul kriterleri:**
- [ ] 3 set × 10 tekrar × 50 kg girilen kaydın hacim sütununda `1500` görünür.
- [ ] Aynı gün girilen 1500 kg ve 1000 kg hacimli iki kayıt için o günün toplamı `2500` olur.
- [ ] Hacim hesaplaması birim testle doğrulanır ve CI'da geçer.

## 3. Hareket ve tarihe göre filtreleme
**Açıklama:** Kayıt listesi hareket adına ve tarih aralığına göre süzülebilir.

**Kabul kriterleri:**
- [ ] "Bench Press" seçildiğinde yalnızca bu hareketin kayıtları listelenir.
- [ ] Tarih aralığı verildiğinde aralığın dışındaki kayıtlar görünmez.

## 4. Hareket bazlı gelişim grafiği
**Açıklama:** Seçilen hareket için zaman içindeki en yüksek ağırlık ve toplam hacim çizgi grafikte gösterilir.

**Kabul kriterleri:**
- [ ] Farklı tarihlerde girilen 3 kayıt grafikte 3 nokta olarak görünür.
- [ ] Kaydı olmayan bir hareket seçildiğinde "veri yok" mesajı gösterilir.

## 5. Kişisel rekor (PR) tespiti
**Açıklama:** Bir harekette o ana kadarki en yüksek ağırlık geçildiğinde kayıt "PR" rozetiyle işaretlenir.

**Kabul kriterleri:**
- [ ] Önceki en yüksek 80 kg iken 85 kg girilen kayıt "PR" olarak işaretlenir.
- [ ] 80 kg'a eşit ya da daha düşük bir kayıt PR sayılmaz.

## 6. Kayıt düzenleme ve silme
**Açıklama:** Hatalı girilen kayıt düzeltilebilir veya silinebilir.

**Kabul kriterleri:**
- [ ] Silinen kayıt listeden ve günlük toplam hacimden düşer.
- [ ] Düzenlenen kaydın yeni değerleri listede ve hacimde görünür.

## 7. Ekipman / hareket listesi yönetimi
**Açıklama:** Kullanıcı kendi salonundaki makineleri ve hareketleri tanımlayabilir.
Kayıt formu bu listelerden seçim önerir.

**Kabul kriterleri:**
- [ ] Yeni eklenen ekipman kayıt formundaki öneriler arasında görünür.

## 8. Antrenman şablonları
**Açıklama:** Kullanıcı sık yaptığı antrenmanı (ör. "Push günü") hareket listesi olarak
şablona kaydeder. Set, tekrar ve ağırlık isteğe bağlıdır. Şablon tek tıkla bugünün
antrenmanına yüklenir; şablonlar listelenebilir ve silinebilir.

**Kabul kriterleri:**
- [ ] Kaydedilen şablon, hareketleriyle birlikte Şablonlar sayfasında listelenir.
- [ ] Tüm değerleri dolu bir şablon "Bugüne yükle" ile bugünün tarihli kayıtlarına eklenir.
- [ ] Değeri eksik bir şablon yüklenirken önce eksik değerler sorulur; eksikken kayıt eklenmez.
- [ ] Silinen şablon listeden kalkar, şablondan eklenmiş kayıtlar silinmez.
