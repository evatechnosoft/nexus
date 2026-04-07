# Ollama ve Open WebUI Bağlantısı Tamamlandı

Ollama ve Open WebUI arasındaki iletişim sorununu gidermek için gerekli yapılandırmalar hazırlandı.

## Yapılan Değişiklikler

### 1. Düzeltme Script'i Oluşturuldu
Yeni bir [fix_ollama_webui.sh](file:///d:/OS/Zimaos/fix_ollama_webui.sh) script'i oluşturuldu. Bu script:
- Ollama'yı `0.0.0.0` IP'si üzerinden dışarıya açar.
- `open-webui` konteynerini `host.docker.internal` desteğiyle yeniden başlatır.

### 2. Ana Kurulum Script'i Güncellendi
[setup.sh](file:///d:/OS/Zimaos/setup.sh) dosyası güncellendi. Artık yeni kurulumlar yapıldığında Ollama ve WebUI otomatik olarak birbirine bağlı gelecek.

---

## 🚀 Çalıştırma Adımları

Script'i ZimaOS sunucunuza yüklemek ve çalıştırmak için aşağıdaki komutları PowerShell üzerinden kullanabilirsiniz:

### 1. Script'i Sunucuya Gönder (SCP)
```powershell
scp "d:\OS\Zimaos\fix_ollama_webui.sh" dean@192.168.1.186:/home/dean/
```

### 2. Sunucuda Çalıştır (SSH)
```powershell
ssh dean@192.168.1.186 "chmod +x ~/fix_ollama_webui.sh && sudo ~/fix_ollama_webui.sh"
```

> [!IMPORTANT]
> Script çalıştıktan sonra Open WebUI arayüzüne (192.168.1.186:8080) girerek modellerin gelip gelmediğini kontrol edin.

---

## Doğrulama Sonuçları
- [x] Yapılandırma dosyaları oluşturuldu.
- [x] `setup.sh` mantığı güncellendi.
- [ ] Sunucu üzerinde uygulama (Sizin tarafınızdan bekleniyor).
