SahinLabs Course Production Tool
==================================

Kurs script ve ses dosyalarini uretmek icin komut satiri araci.
Her ders icin: kurs icerigi + bootcamp transkriptleri → Claude script → ElevenLabs ses (MP3)


KURULUM
-------
1. Python bagimlilikları yukle:
   pip install -r requirements.txt

2. .env dosyasi olustur ve API anahtarlarini ekle:
   ANTHROPIC_API_KEY=sk-ant-...
   ELEVENLABS_API_KEY=sk_...

3. Kurs icerigi hazir olmali:
   sources/sahinlabs_course.txt   (kurs modulleri ve dersler)


KLASOR YAPISI
-------------
course-production/
├── generate.py              ← Ana giris noktasi (buradan calistir)
├── config.py                ← Yol ve API sabitleri
├── src/
│   ├── context_builder.py   ← Ders baglami olusturma
│   ├── script_generator.py  ← Claude ile script uretimi
│   ├── audio_generator.py   ← ElevenLabs ile MP3 uretimi
│   ├── lesson_tracker.py    ← Ders durumu takibi (JSON)
│   ├── review_ui.py         ← Script onay arayuzu
│   └── ...
├── sources/
│   ├── sahinlabs_course.txt ← Kurs icerigi (zorunlu)
│   └── lesson_status.json   ← Ders durumu veritabani (otomatik olusur)
├── scripts/                 ← Uretilen scriptler (*.md)
└── audio/                   ← Uretilen ses dosyalari (*.mp3)


KULLANIM
--------

1. Tum derslerin durumunu gor:
   python generate.py --list

   Cikti: Her ders icin durum (❌ pending / 📝 scripted / ✅ audio_done)
   Modullere gore gruplu, ozel durum sayaci ile.


2. Tek komutla tam ders akisi:
   python generate.py --lesson M0L1

   Yaptiği işlemler:
   - Ders baglami olusturur (kurs icerigi + bootcamp transkriptleri)
   - Claude ile Turkce/Ingilizce script uretir
   - Scripti gostererek onay bekler (kabul / revize / atla)
   - Kabul sonrasi "Ses uretilsin mi? (y/n)" sorar
   - Evet ise: ElevenLabs Jon sesiyle MP3 kaydeder
   - Ders durumunu gunceller

   LESSON_ID formati: M{modul}L{ders} — ornegin M0L1, M1L3, M5L2


3. API cagrisı yapmadan baglam incele (debug):
   python generate.py --dry-run M0L1

   Ders outline + bootcamp alintilari gosterir.
   Token tahminini verir. Hicbir API cagrisi yapmaz.


4. Mevcut script icin sadece ses uret:
   python generate.py --audio M0L1

   scripts/M0L1_*.md dosyasini okur → MP3 uretir.
   Script onceden onaylanmis olmali.


5. Interaktif mod (modul/ders secer):
   python generate.py

   Modul secimi → ders secimi → script akisi → onay → ses secenegi


DERS ID FORMATI
---------------
  M0L1   → Modul 0, Ders 1  (Foundations — Welcome)
  M1L3   → Modul 1, Ders 3  (Character Creation — Golden Dataset)
  M5L6   → Modul 5, Ders 6  (Scaling — The Exit)

  Mevcut dersler:
  - MODULE 0: M0L1, M0L3, M0L4, M0L5
  - MODULE 1: M1L1 - M1L5
  - MODULE 2: M2L1 - M2L5
  - MODULE 3: M3L1 - M3L7 (M3L5.5 dahil)
  - MODULE 4: M4L1 - M4L5
  - MODULE 5: M5L1 - M5L6


TIPIK CALISMA AKISI
-------------------
1. python generate.py --list         → Hangi dersler bekliyor?
2. python generate.py --dry-run M1L1 → Baglam nasil gorunuyor? (opsiyonel)
3. python generate.py --lesson M1L1  → Script uret, onaylarsan ses de uret
4. python generate.py --list         → Guncellenmis durumu kontrol et


TIPIK HATA COZUMLERI
---------------------
"Course file not found"
  → sources/sahinlabs_course.txt dosyasinin var oldugunu kontrol et

"ElevenLabs API error (401)"
  → .env dosyasindaki ELEVENLABS_API_KEY degerini kontrol et

"Claude API error / APIError"
  → ANTHROPIC_API_KEY degerini kontrol et
  → Sistem otomatik olarak 10sn sonra 1 kez daha dener

Ders zaten scripted/audio_done ama yeniden uretmek istiyorsun:
  → python generate.py --lesson M0L1 calistir
  → "Yeniden uretilsin mi? (y/n)" sorusuna y de


TEST
----
   python -m pytest tests/ -v

   Tum testler (49 adet) API cagrisı yapmadan calisir (mock kullanır).
