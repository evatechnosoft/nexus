# NPM Setup Walkthrough on ZimaOS

ZimaOS üzerinde Nginx Proxy Manager (NPM) yapılandırması başarıyla tamamlanmıştır. Uygulanan adımlar ve sonuçlar aşağıdadır:

## Yapılan İşlemler

1. **Admin Paneli Erişimi:** NPM'in 81 portu üzerinden yönetim paneline erişim sağlandı.
2. **Port Çakışması Çözümü:** ZimaOS'un (CasaOS) varsayılan 80 portu ile NPM arasındaki çakışma, ZimaOS web arayüzünün **85** portuna taşınmasıyla giderildi.
3. **Port Yönlendirme:** Modem üzerinden 80 ve 443 portları ZimaOS cihazına yönlendirildi.
4. **Proxy Host Yapılandırması:** Alan adı (domain), NPM üzerinden ilgili yerel servise başarıyla yönlendirildi.
5. **SSL (Let's Encrypt):** Port çakışması ve "Already In Use" hataları giderildikten sonra Let's Encrypt sertifikası başarıyla oluşturuldu.

## Doğrulama Sonuçları

- [x] `http://<domain>` üzerinden siteye erişim sağlandı.
- [x] `https://<domain>` üzerinden SSL sertifikası (yeşil kilit) doğrulandı.
- [x] ZimaOS arayüzüne `http://<IP>:85` üzerinden erişim doğrulandı.

## Gelecek Adımlar

- Diğer servisler için sub-domainlerin (örn: `panel.domain.com`, `app.domain.com`) NPM üzerinden eklenmesi.
- Prodüksiyon sitesinin yayınlanması.
