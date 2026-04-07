Iliskisiz gorevler arasinda handoff kaydet /compress /clear kullan
A konusundaki baglami B konusuna tasima
Uzun chat'teki her mesajı yeni chat'tekinden USTEL olarak pahali
Konu degistiginde yeni sohbet = aninda tasarruf
Tek komut, en buyuk etki
Her bagli MCP sunucusu = mesaj basina ~18.000 token
/mcp calistir -> gerekmeyenleri kapat
MCP yerine CLI kullan (daha hizli + daha ucuz)
Ornek: Google Calendar MCP -> Google Workspace CLI
Tek bir sunucu kapatmak = her mesajda 18K token tasarruf
Prompt'lari Tek Mesajda Birlestir
YANLIS: 3 ayri mesaj = 3x maliyet
DOGRU: "Ozetle + sorunlari cikar + duzeltme oner" -> tek mesaj
Claude yanlis yaptiysa -> orijinal mesaji duzenle + regenerate
Takip mesaji gecmise kalici eklenir
Duzenleme ise kotu degisimi tamamen siler
Claude.md'ye ekle: "%95 guvene ulasana kadar soru sor"
En buyuk token israfii yanlis yone gidip kod yazmasi
Sonra hepsini cope atman = cift maliyet
Once planla -> sonra uygula = en ucuz yol
Planlama 100 token, yanlis kod 10.000 token
/context -> Token'larini ne yiyor? (gecmis, MCP, dosyalar)
/cost -> Gercek token kullanimi ve tahmini harcama
Bos oturumda bile 51.000 token harcaniyor!
Sistem prompt + araclar + agents + skill'ler + memory
Gorunmezi gorunur yapar - ilk adim her zaman olemek
Terminal'de surekli gosterge: model, yuzde, token sayisi
Hangi modeli kullandigini her zaman gor
Baglam yuzdesini anlik takip et
Token sayisi limitle orantili
Farkinda olmak = kontrol etmek
claude.ai -> kullanim dashboard'u surekli acik
Her 20-40 dakikada kontrol et
Reset'e ne kadar kaldigini bil
Otomasyon kur: 30dk'da bir Slack/SMS uyarisi
Limiti bilmeden optimize edemezsin

Prompt'u gonderip gitme - ozellikle uzun gorevlerde izle
Yanlis yone gidiyorsa -> hemen durdur
Kendi dongusune giriyorsa -> durdur
Ayni dosyalari tekrar okuyorsa -> durdur
Kotu bir dongude token'larin %80'i sifir deger uretir

200 satirin altinda tut - her mesajda yeniden okunur
1000 satirlik claude.md = "merhaba" bile 1000 satir token
Indeks gibi dusuni buyuk veriyi gosterme, nerede oldugunu soyle
claude.md -> "Marka sesi icin/context/brand-voice.md oku"
Claude sadece gerektiğinde o dosyaya gider = devasa tasarruf
YANLIS: "Iste tum repo'm, bug'i bul"
DOGRU: "auth.js'deki verifyUser fonksiyonunu kontrol et"
@dosya-adi ile spesifik dosyayi goster
Tum repo = 100.000 token, tek dosya = 2.000 token
Cerrahi hassasiyet = 50x tasarruf
/compact Ineyi koruması gerektiğini belirt]
Otomatik compact %95'te tetiklenir - cok gec!
%60'ta manuel compact yap
Ust uste 3-4 compact sonrasi kalite duser
Cozumi ozet al -> /clear -> ozeti yapistirip devam et
Claude Code'un prompt cache'i = 5 dakika zaman asimi
5 dk'dan uzun mola -> sonraki mesaj her seyi sifirdan isler
Mola oncesi -> /compact veya /clear yap
Cache'i kaybetmek = tam maliyet odeme
Kisa mola = cache korunur, uzun mola = onlem al
Claude shell komutu calistirdiginda TUM cikti baglama girer
200 commit'lik git log = devasa token
Bildigin projede gereksiz komutlari deny et
Claude'un calistirdigi komutlarin cikti boyutunu dusun
git log --oneline -5 vs git log = 100x fark
Sonnet Varsayılan, cogu kodlama isi (%60-70)
Haiku Sub-agent'lar, formatlama, basit gorevler (%15-20)
Opus Derin mimari planlama (%10-20)
Codex-> Kod inceleme (Claude token'i harcamaz)
Opus'u %20'nin altinda tut
Token'larin %80'ini ucuz modelde harca
Sonnet %60-70
Haiku %15-20
Opus %10-20
Agent is akislari tek agent'tan 7-10x daha fazla token harcar
Her sub-agent kendi tam baglamiyla uyanir
Tek seferlik gorevleri sub-agent'a devret (Haiku ile)
Arastirma/kesif -> sub-agent -> sadece ozet donsun
Agent teams harika ama cok pahali -> dikkatli kullan
Yogun Saatleri Anla
Yoguni Hafta ici 08:00-14:00 ET -> Limit hizli tukenir
Sakin: Ogleden sonra, aksam, hafta sonu -> Normal surer
Buyuk refactor, multi-agent -> sakin saatlere planla
Reset'e yakın + kapasite svarsa -> sprint yap, doldur
Limit'e yakın + zaman varsa -> mola ver, tam butceyle dön
08:00-14:00 ET (YOGUN)
14:00-08:00 ET (SAKIN)
Claude.md sonuna "Applied Learning" bolumu ekle
Tekrarlayan hatalar -> otomatik tek satir bullet ekle
Her bullet 15 kelimeden kisa olsun
Kaydedilen karar = bir daha yazmak zorunda olmadigin paragraf
Sik kontrol et - sismemeli!
19
.claudeignore Dosyasi Kullan
.gitignore gibi calisir - Claude'un okumamasini istedigin dosyalari listele
node modules/, dist/, build/, *.log -> her kesif turunda binlerce token tasarruf
Claude dosya ararken bu klasorleri tamamen atlar
20
Skill'leri Lazy-Load Yap
Global'deki her skill HER mesajda yeniden yuklenir - kullanmasan bile
10 global skill = her mesajda 10 skill'in token'i
Cogu skill'i proje seviyesine tasi: 2 global + 8 proje = buyuk tasarruf
Headless Mode (--print)
claude --print "bu fonksiyondaki bug'i bul" < auth.js
Oturum overhead'i sifir - claude.md, MCP, skill yuklemesi yok
Tek seferlik isler icin ideali hizli + ucuz
![checklisti uyarla bize](image-1.png)
dry-run tarama yap
nasıl kullanılacağını yapımıza nasıl oturacağını açıkla planla  hatırlat 
