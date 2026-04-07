# ZimaOS Nginx Proxy Manager (NPM) Bağlantı Rehberi

Bu rehber, ZimaOS üzerinde kurduğunuz Nginx Proxy Manager'a nasıl erişeceğinizi ve kendi alan adınızı (domain) nasıl bağlayacağınızı adım adım açıklar.

## 1. Yönetim Paneline Erişim
Nginx Proxy Manager varsayılan olarak **81** portunu kullanır.

- **Adres:** `http://<ZimaOS-IP-Adresiniz>:81`
- **Varsayılan Giriş Bilgileri:**
  - **Email:** `admin@example.com`
  - **Şifre:** `changeme`

> [!IMPORTANT]
> İlk girişte sistem sizden bu bilgileri güncellemenizi isteyecektir. Güvenliğiniz için güçlü bir şifre belirleyin.

---

## 2. Port Yönlendirme (Modem Ayarları)
Dış dünyadan domaininizle erişim sağlamak için modeminizden ZimaOS cihazınıza şu portları yönlendirmeniz gerekir:

| Dış Port | İç Port (ZimaOS) | Protokol | Açıklama |
| :--- | :--- | :--- | :--- |
| 80 | 80 | TCP | HTTP trafiği için |
| 443 | 443 | TCP | HTTPS (SSL) trafiği için |

> [!WARNING]
> **ZimaOS Port Çakışması:** Eğer ZimaOS arayüzü de 80 veya 443 portunu kullanıyorsa NPM çalışmayabilir. Bu durumda ZimaOS ayarlarından web arayüz portunu (örneğin 85'e) değiştirmeniz gerekebilir.

---

## 3. Domain Bağlama (Proxy Host Ekleme)
Alan adınızı bir servise yönlendirmek için NPM panelinde şu adımları izleyin:

1. **Hosts** -> **Proxy Hosts** -> **Add Proxy Host** butonuna tıklayın.
2. **Details Sekmesi:**
   - **Domain Names:** `domaininiz.com` veya `sub.domaininiz.com` yazın.
   - **Scheme:** `http` (veya servisiniz https ise https).
   - **Forward Name/IP:** ZimaOS'un yerel IP'sini veya servis Docker üzerindeyse konteyner adını yazın.
   - **Forward Port:** Yönlendirmek istediğiniz servisin portu (örn: 8080).
   - **Block Common Exploits:** İşaretlemeniz önerilir.
3. **SSL Sekmesi (HTTPS Aktifleştirme):**
   - **SSL Certificate:** `Request a new SSL Certificate` seçin.
   - **Force SSL:** İşaretleyin (HTTP'yi HTTPS'e zorlar).
   - **HTTP/2 Support:** İşaretleyin (Hız için).
   - **I Agree to the Let's Encrypt Terms:** İşaretleyin.
4. **Save** butonuna basın.

> [!TIP]
> Eğer "Save" dediğinizde hata alırsanız, önce SSL seçmeden (None) kaydedin. Siteye `http` üzerinden erişebiliyorsanız her şey yolundadır, sonra tekrar "Edit" diyerek SSL eklemeyi deneyin.

---

## 5. "Internal Error" Hatası ve Çözümü
NPM panelinde "Internal Error" alıyorsanız genellikle şu üç neden den biridir:

### A. SSL (Let's Encrypt) Hatası
Eğer hatayı SSL sekmesinde "Save" dediğinizde alıyorsanız:
- Modemden **80 ve 443** portlarının ZimaOS IP'sine yönlendiğinden emin olun.
- Alan adınızın (DNS A kaydı) doğru IP'ye baktığını kontrol edin.
- **Çözüm:** Önce SSL kısmını "None" seçerek kaydedin. Eğer SSL'siz kaydediliyorsa sorun kesinlikle SSL onayındadır.

### B. ZimaOS Port Çakışması
ZimaOS varsayılan olarak 80 portunu kullanıyor olabilir.
- **Kontrol:** Tarayıcıya sadece IP yazdığınızda ZimaOS açılıyorsa port çakışması vardır.
- **Çözüm:** ZimaOS ayarlarından web portunu (örn: 85) değiştirin.
### E. DNS ve "Connection Timed Out" Sorunu
Görseldeki hata, Let's Encrypt servisinin sizin sunucunuza (port 80 üzerinden) ulaşamadığını gösterir.

1. **A Record (A Kaydı):** Domain sağlayıcınızın (GoDaddy, Namecheap, Cloudflare vb.) panelinde `evaitec.com` için bir **A Kaydı** oluşturun ve bunu evinizin/serverınızın **Dış IP (Public IP)** adresine yönlendirin. 
   - *Not:* NameServer (NS) değiştirmenize gerek yok, sadece A kaydı yeterlidir.
2. **Cloudflare Kullanıyorsanız:** Eğer DNS için Cloudflare kullanıyorsanız, turuncu bulutu (**Proxy**) kapatıp "DNS Only" (Gri bulut) yapmanız gerekir. SSL alındıktan sonra tekrar açabilirsiniz.
3. **Port 80:** Modeminizden 80 portunu ZimaOS'un yerel IP'sine yönlendirdiğinizden %100 emin olun. Çoğu modemde bu ayar "NAT" veya "Port Forwarding" altındadır.

### F. Double NAT (İç İçe Modem) Sorunu
AP (`192.168.1.1`) ve Ana Modem (`192.168.0.1`) şeklinde iki cihazınız olması, trafiğin iki kez filtrelendiği anlamına gelir. SSL onayı için şu zinciri kurmalısınız:

1. **Ana Modem (192.168.0.1) Üzerinde:**
   - 80 ve 443 portlarını **AP'nin WAN IP'sine** (192.168.0.x ağındaki IP'si) yönlendirin.
2. **AP (192.168.1.1) Üzerinde:**
   - 80 ve 443 portlarını **ZimaOS'un Yerel IP'sine** (192.168.1.x ağındaki IP'si) yönlendirin.

> [!TIP]
> **En Kolay Yol:** Eğer mümkünse AP'yi (192.168.1.1) "Bridge Mode" (Köprü Modu) veya "Access Point Mode" olarak ayarlayın. Bu durumda NAT işlemini sadece ana modem yapar ve tek bir yerden port açmanız yeterli olur.


