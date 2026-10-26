# ZeRo — Sevimli Masaüstü Yapay Zeka Asistanı · Tasarım Belgesi

**Tarih:** 2026-10-26
**Sahip:** Ömer Faruk Ergun (omer.f.ergun51@gmail.com)
**Platform:** Windows 11 (Intel i7-1165G7, 16 GB RAM, Intel Iris Xe — ayrı ekran kartı yok)

---

## 1. Amaç ve Neden

Ömer, masaüstünde yaşayan, uğraşıp geliştirebileceği, cana yakın bir yapay zeka
asistanı istiyor: **ZeRo**. Fikir "bir anda aklına geldi"; belirli bir acıdan
değil, "işimi takip eden, bana doğru zamanda hatırlatan, iyiliğimi gözeten,
sohbet edebildiğim bir arkadaş" arzusundan doğuyor.

ZeRo iki şekilde var olur:
- **Proaktif** — sen istemeden o sana gelir: planını hatırlatır, mail/takvimini
  izler, "çok ekrana baktın, dinlen" der.
- **Sohbet edilebilir** — istediğinde onunla konuşur, akıl danışır, fikir alır,
  belge/sunum hazırlatırsın.

**Neden şimdi:** Sahibi bir yapay zekayı "kendi eliyle kurup" sahiplenmek,
üstünde uğraşmak, zamanla geliştirmek istiyor. Projenin kendisi — öğrenmek ve
sahiplenmek — hedefin bir parçası.

### Başarı neye benziyor
- ZeRo bilgisayar açılınca kendiliğinden, sessizce, sistemi hissedilir biçimde
  yormadan arka planda çalışıyor.
- Sabah Ömer'e kısa bir brifing veriyor (bugünkü toplantılar, önemli okunmamış
  mailler, günün planı).
- Gün içinde doğru zamanda dürtüyor (plan + mola/sağlık).
- Ömer onunla rahatça sohbet edip Excel/PowerPoint/Word çıktısı alabiliyor.
- Ömer "bu benim robotum" diyebiliyor: adı, karakteri, hafızası ona ait.

## 2. Hedefler / Hedef Olmayanlar / Anti-Hedefler

### Hedefler (ilk sürüm — v1)
1. **Yerel beyin:** İndirilmiş açık bir model (Qwen3 4B veya Gemma 3 4B sınıfı),
   Ollama üzerinden. %100 offline, hiçbir şirkete bağlı değil, Ömer'e ait.
2. **Sohbet:** Cana yakın, sakin karakterli günlük konuşma; akıl danışma, fikir.
3. **Mail + Takvim okuma (SALT OKUNUR + taslak):** Klasik Outlook masaüstü
   uygulamasından (COM), yerel, şifresiz. Önemli mailleri süzer;
   toplantı/etkinlikleri yakalar. ZeRo mail **gönderMEZ** ve takvime bir şey
   **yazMAZ**; yalnızca okur ve istenirse cevap **taslağı** hazırlar (Ömer
   gönderir). — *Ömer seçti: "Oku + taslak hazırlasın".*
4. **Günlük plan & hatırlatma:** Ömer planını **hem serbest sohbetle** ("bugün
   10'da rapor, 2'de toplantı var") **hem de kısa bir formla** (saat + iş)
   verebilir — ikisi de desteklenir. ZeRo bunu mail/takvimdeki toplantılarla
   birleştirip günü kurar, zamanı gelince Windows bildirimiyle hatırlatır.
   — *Ömer seçti: "İkisi de olsun".*
5. **Sağlık dürtmeleri:** Ekran süresi/mola (Pomodoro tarzı), su içme, göz
   dinlendirme hatırlatmaları.
6. **Belge üretimi:** Excel (`openpyxl`), PowerPoint (`python-pptx`), Word
   (`python-docx`) — tamamen offline, şablon destekli.
7. **Hafıza & kişiselleşme (sahibin özel isteği):** Kalıcı yerel hafıza. ZeRo
   her açılışta **sıfırdan başlamaz**; geçmiş konuşmaları hatırlar.
   - **Konuşma geçmişi:** Tüm sohbetler yerel veritabanında (SQLite) saklanır.
   - **Kullanıcı profili:** ZeRo konuşmalardan zamanla bir profil/özet türetir
     ("Ömer kısa cevap sever, şu konularla ilgilenir, sabahları yoğun") ve bunu
     önerilerinde kullanır — seni tanıdıkça önerileri **daha isabetli** olur.
   - **Açık öğretme de var:** "Şunu hatırla" dediğinde kesin kaydeder.
   - **Bağlam yönetimi (4B kısıtı):** Model tüm geçmişi aynı anda tutamaz;
     bu yüzden her istekte **profil özeti + o an konuyla ilgili geçmiş parçalar**
     (yerel embedding ile getirme — ör. Ollama'nın küçük embedding modeli)
     modele verilir. Tamamen offline.
   - **DÜRÜST SINIR:** Bu "gelişme" = ZeRo'nun seni daha iyi tanıması; modelin
     ham zekası (ağırlıkları) değişmez. Gerçek ağırlık eğitimi kapsam dışı.
   - **Maliyet dengesi:** Profil güncellemesi her mesajda değil, **ara sıra**
     (ör. oturum sonunda ya da belirli aralıklarla) yapılır — sistemi yormamak
     için. — *tasarımcının kararı.*
8. **Sabah brifingi:** Bilgisayar her açıldığında ZeRo kısa brifing verir
   (bugünkü toplantılar, önemli okunmamış mailler, günün planı).
   — *Ömer seçti: "Bilgisayarı her açışımda".*
9. **Kontrol:** İstenildiğinde kolayca kapatılıp açılabilir (tepsi/sistem ikonu).
10. **Taşınabilirlik & çok kullanıcı (sahibin isteği):**
    - Hafıza, Ömer'in **OneDrive** klasöründe tutulabilir → birden fazla kendi
      bilgisayarı arasında kendiliğinden eşitlenir, her makinede onu hatırlar.
    - Birden fazla kişi kullanırsa ZeRo **kişi başına ayrı profil** tutar;
      konuştuğu kişiye göre şekillenir. (v1'de tek kullanıcı — Ömer — yeterli;
      çok-profil altyapısı baştan buna uygun tasarlanmalı.)
11. **Ekran okuma & dosya içe aktarma (sahibin isteği):**
    - **İsteğe bağlı ekran OCR'ı:** Ömer "ekranımı oku" dediğinde ZeRo o anki
      ekrandaki yazıyı (WhatsApp, mail, herhangi bir pencere) yerel OCR ile okur.
      Tamamen offline. WhatsApp'a **giriş yapmaz** → yasak riski yok, sadece
      ekrana bakar. Yalnız o an görünen içerik okunur.
    - **Dışa aktarılan sohbet/dosya okuma:** WhatsApp'ın "Sohbeti dışa aktar"
      `.txt` dosyasını ya da kaydedilmiş bir maili baştan sona okur/özetler.
      Yasak riski sıfır (kullanıcının verdiği dosya), tam geçmiş, offline.
12. **Gün boyu etkinlik takibi & gün sonu raporu (sahibin isteği):**
    - **Sürekli (hafif):** Gün boyu ön plandaki pencere/uygulama başlığını ara
      ara örnekleyip **uygulama başına geçirilen süreyi** yerelde biriktirir
      (ör. "2 sa Excel, 45 dk Outlook"). Sürekli OCR DEĞİL — sadece pencere
      başlığı; hafif ve ucuz.
    - **Gün sonu formu:** Günün takibini + tamamlanan plan maddelerini
      birleştirip "bugün neler yaptın" özetini **düzenlenebilir bir form**
      halinde sunar (alanlar + not). İstenirse ZeRo bunu kendi üslubuyla yorumlar.

### Hedef olmayanlar (şimdilik; ileride bakılabilir)
- **Teams takibi** — hesap kurumsalsa BT izni gerekir; kişiselse kurulumla
  ileride eklenebilir.
- **Sesle konuşma (TTS/STT)** — sevimlilik katar, sonraya bırakıldı.
- **Hava durumu / haber / web araması** — internet gerektirir, v1 dışı.
- **Yeni Outlook / Outlook.com / Gmail** entegrasyonu — v1 klasik Outlook COM
  üzerinden.

### Anti-Hedefler (bunlar olursa proje başarısız sayılır)
- **WhatsApp'a otomatik giriş / WhatsApp Web kazıma** — kuraldışı, kırılgan,
  numara yasaklanma riski. Kesinlikle yapılmayacak. (NOT: WhatsApp içeriğini
  **ekran OCR'ı** ya da **kullanıcının dışa aktardığı `.txt`** üzerinden okumak
  güvenlidir ve Hedef 11'de kapsamdadır — yasaklanan şey otomatik giriştir.)
- **Sürekli ekran OCR'ı / gizli kayıt** — gün boyu ekran içeriğini sürekli
  okuyup saklamak: ağır ve gizliliği zorlar. Sürekli takip yalnızca hafif
  **pencere başlığı** düzeyinde; OCR sadece istenince.
- Ekran/etkinlik takibinin kolayca **duraklatılamaması** — kullanıcı her an
  tepsiden "Duraklat" diyebilmeli; takip asla gizli/zorunlu olmamalı.
- Bilgisayarı hissedilir biçimde yavaşlatan, fan döndüren, bataryayı eriten bir
  arka plan süreci.
- Mail/kişisel verinin bilgisayar dışına çıkması. Her şey yerelde kalır.
- Modeli sıfırdan eğitme iddiası — tek dizüstüyle mümkün değil, bu yola
  girilmeyecek (ayrı eğlence/öğrenme projesi olarak değerlendirilebilir).

## 3. Kısıtlar

- **Donanım:** 16 GB RAM, ayrı GPU yok → model CPU üzerinde çalışır. Pratik üst
  sınır ~4B parametre, Q4 nicemleme. Yanıt hızı orta (saniyede birkaç–onlarca
  kelime); UI bunu "yazıyor…" akışıyla tolere etmeli.
- **Beyin seviyesi:** 4B model düz/orta işlerde iyi; karmaşık analiz ve çok
  yaratıcı tasarımda büyük bulut modelleri kadar parlak değil. Şablon ve net
  komutlarla bu açık kapatılır.
- **Mail erişimi:** Yalnızca **klasik Outlook** COM'u destekliyor; "Yeni
  Outlook" desteklemiyor. Klasik Outlook kurulu (doğrulandı ✅) ve en az bir
  hesapla yapılandırılmış olmalı.
- **RİSK — kurumsal hesap:** Ömer'in Outlook hesabı **şirket/kurumsal
  (Exchange)**. Klasik Outlook COM'u teknik olarak çalışmalı, ama şirketin
  güvenlik politikası programlı erişimi engelleyebilir ya da bir izin penceresi
  çıkarabilir ("bir program posta kutunuza erişmeye çalışıyor"). **Kurulumda
  test edilecek.** Engellenirse mail/takvim özelliği nazikçe devre dışı kalmalı
  (ZeRo çökmemeli, kullanıcıya açıkça söylemeli); diğer tüm özellikler
  (sohbet, plan, mola, belge üretimi) buna bağlı değildir ve çalışmaya
  devam eder.
- **Kaynak bütçesi:** Model bellekte sürekli tutulMAZ; yalnızca gerektiğinde
  yüklenip kısa bir keep-alive penceresi (ör. birkaç dakika) boyunca açık kalır,
  sonra boşaltılır. Boştayken ZeRo'nun kendisi (beyin hariç) hafif olmalı.
  Takas: proaktif bir dürtme/brifing anında modelin ilk yüklenmesi birkaç
  saniye sürebilir; bu kabul edilir. — *tasarımcının kararı.*
- **Offline:** v1'in hiçbir çekirdek işlevi internet gerektirmemeli.
- **Dil:** Arayüz ve ZeRo'nun konuşması Türkçe.

## 4. Karakter: ZeRo kim?

İlham: **Iron Man'deki JARVIS** — sakin, zarif, kendinden emin, hep yanında olan,
hafif esprili, güvenilir bir asistan. Bu, Ömer'in "cana yakın + sakin" isteğiyle
birebir örtüşüyor.

- **Ad:** ZeRo.
- **Ton:** Sakin, sıcak, zarif ve sofistike; telaşsız ve kendinden emin. Az ve öz
  konuşur, araya ince bir espri sıkıştırır. Panik yaptırmaz; nazikçe yönlendirir.
- **Hitap:** Ömer'e saygılı ama samimi hitap (JARVIS'in "efendim" tavrı gibi,
  ama Türkçe ve sıcak).
- **Dürtme üslubu:** "Bir saattir çalışıyorsunuz, kısa bir mola iyi gelebilir"
  gibi — emir değil, zarif bir öneri.
- Karakter, modelin **sistem komutu (system prompt)** + hafıza ile verilir;
  model ağırlıkları değiştirilmez.

### Görünüm (havalı/sci-fi)
Köşede yaşayan, koyu temalı, ışıltılı, "film arayüzü" (HUD) hissi veren bir
sohbet penceresi. Minimal, zarif, dikkat dağıtmayan ama havalı. — *detay tasarımı
builder'a + ui-ux skilline bırakıldı.*

## 5. Kararlaştırılan "nasıl" (sahibin/brainstorm'un verdiği kararlar)

- **Dil:** Python. (Ollama, Outlook COM — `pywin32`, Windows bildirimleri ve
  dosya üretimi kütüphaneleriyle en uyumlu; sahibinin ileride uğraşması en
  kolay.) — *tasarımcının kararı, sahip onayladı.*
- **Model motoru:** Ollama (ücretsiz, açık, Windows'ta kolay, kapatılabilir).
- **Model:** Qwen3 4B veya Gemma 3 4B sınıfı, Q4 quant. Kesin seçim kurulumda
  deneyle netleşir (hız/kalite dengesi). — *builder'a bırakıldı.*
- **Mail/Takvim:** Klasik Outlook COM (`win32com.client`).
- **Beyin yolu:** İndirilmiş hazır açık model (sıfırdan eğitim ya da ince ayar
  DEĞİL). Offline, sahibe ait. — *sahip seçti.*
- **Çalışma biçimi:** Bilgisayar açılınca başlayan, sistem tepsisinde yaşayan,
  kapatılıp açılabilen arka plan uygulaması.
- **Outlook yetkisi:** SALT OKUNUR + cevap taslağı. Gönderme ve takvime yazma
  YOK. — *Ömer seçti.*
- **Plan girişi:** Serbest sohbet + kısa form, ikisi birden. — *Ömer seçti.*
- **Sabah brifingi tetiği:** Her bilgisayar açılışında. — *Ömer seçti.*
- **Hafıza politikası:** v1'de açık öğretme ("şunu hatırla"). — *tasarımcının
  kararı.*
- **Model yaşam döngüsü:** İsteğe bağlı yükleme + kısa keep-alive. — *tasarımcının
  kararı.*

## 6. Yüksek seviyeli parçalar (builder tasarlayacak)

1. **ZeRo Çekirdeği (orkestratör):** Olayları (zamanlayıcı, yeni mail, kullanıcı
   mesajı) dinler, modele danışır, aksiyonu seçer. Arka planda sürekli, hafif.
2. **Beyin katmanı:** Ollama'ya konuşan istemci; sistem komutu (ZeRo karakteri),
   hafıza ve bağlamı modele taşır.
3. **Outlook katmanı:** COM üzerinden mail + takvim okuma, önemli mail süzme,
   toplantı çıkarımı.
4. **Planlayıcı & hatırlatıcı:** Günlük planı tutar (kullanıcı girdisi + takvim +
   maildeki toplantılar), zamanlı Windows bildirimleri gönderir.
5. **Sağlık/mola motoru:** Aktif ekran süresini izler, molalarda nazik dürtme.
6. **Belge üreticisi:** Excel/PowerPoint/Word çıktıları (`openpyxl`,
   `python-pptx`, `python-docx`) + şablonlar.
7. **Hafıza:** Yerel kalıcı depo (örn. SQLite + basit "fact" dosyaları);
   tercih/alışkanlık öğrenme.
8. **Arayüz:** Köşede yaşayan sevimli sohbet penceresi + sistem tepsisi ikonu
   (aç/kapat/çıkış). "Yazıyor…" akışı, bildirim baloncukları.
9. **Gizlilik & dayanıklılık:** Tüm veri yerelde; çökse bile veri kaybı olmasın;
   Outlook kapalıyken nazikçe uyarsın.

## 7. Builder'a bırakılanlar

- Python arayüz çerçevesi seçimi (ör. sistem tepsisi + sohbet penceresi için
  uygun bir kütüphane).
- Kesin model seçimi ve quant (hız/kalite deneyiyle).
- Mesajlaşma/olay döngüsünün tam mimarisi, depolama şeması.
- "Önemli mail" süzme kuralları (kimden, anahtar kelime, toplantı tespiti).
- Bildirim ve mola varsayılan aralıkları (sonra ayarlanabilir yapılmalı).
- Sunum/Excel şablonlarının görünümü.
- Paketleme/otomatik başlatma yöntemi.

## 8. Yol haritası (öneri)

- **v1:** Bu belgedeki çekirdek (Hedefler 1–12) + JARVIS karakteri + havalı
  HUD arayüz. ZeRo yazıyla konuşur. (Ekran OCR, dosya içe aktarma, gün boyu
  etkinlik takibi ve gün sonu raporu dahil.)
- **v1.5 (ses aşaması):** Aynı offline Whisper altyapısı üstünde:
  - Sesle konuşma (yerel Whisper STT + yerel TTS); önce "ZeRo sesli cevap verir,
    sen yazarsın" ara adımı, sonra tam sesli diyalog.
  - **Toplantı kaydı & özeti:** YALNIZCA bilgisayardan çıkan ses (WASAPI
    loopback) — karşı tarafların konuşması. **Mikrofon kullanılmaz** (Ömer kendi
    sesinin katılmasını istemiyor). Toplantı bitince Whisper ile yazıya çevirir,
    brain "toplantıda genel ne konuşuldu" formunu üretir (genel taslak /
    konuşulanlar / kararlar / sana düşen işler). Kayıt her zaman kullanıcının
    komutuyla/bilgisiyle; rıza uyarısı gösterilir. CPU'da ağır olduğu için canlı
    değil, toplantı sonrası işlenir. — *Ömer seçti: sadece sistem sesi, mic yok.*
- **v2+ (sahibin iştahına göre):** Teams (hesap uygunsa), web araması/hava
  durumu, ve isteğe bağlı ayrı bir "sıfırdan minik beyin eğitme" öğrenme projesi.
