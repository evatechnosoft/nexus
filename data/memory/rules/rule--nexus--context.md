---
id: rule--nexus--context
type: workflow
context: global
extends: rule--nexus--master
description: Context yönetimi ve interaktif /compress protokolü.
---
# NEXUS CONTEXT MANAGEMENT PROTOCOL

Bu kural, AI'nın "akıl karışıklığını" önlemek için interaktif kontrol noktaları sağlar.

## 🏁 OTURUM BAŞLANGICI (WELCOME PROTOCOL)
Her yeni oturum başladığında AI **mutlaka**:
1. `data/memory/sync/resume-state.md` dosyasını okumalıdır.
2. `ask_user` kullanarak kullanıcıya "Resume Options" butonlarını sunmalıdır.
3. Kullanıcı seçim yapana kadar büyük işlemlere başlamamalıdır.

## 🤖 AI TALİMATLARI (AUTO-ACTION)
1. Her 4-5 soruda bir (veya turn tracker uyarı verdiğinde), AI **mutlaka** `ask_user` kullanarak kullanıcıya seçenekler sunmalıdır.
2. Kullanıcı "Mühürle & Compress" seçerse, AI `python scripts/nexus-compress.py` çalıştırmalıdır.

## 🔘 İNTERAKTİF BUTONLAR (CHOICES)
- **🚀 Mühürle & Compress:** Tüm hafızayı günceller, dream raporu alır ve seansı kapatmaya hazırlar.
- **⏳ 2 Turn Daha Devam:** Mevcut iş bitmediyse süreyi uzatır.
- **💾 Sadece Kaydet:** Sadece kuralları günceller ama seansı sıfırlamaz.

## 📊 KONTROL NOKTASI
- [ ] Turn Tracker takip ediliyor mu?
- [ ] 4. turn sonrası seçenekler sunuldu mu?
- [ ] Handoff dosyası güncel mi?
