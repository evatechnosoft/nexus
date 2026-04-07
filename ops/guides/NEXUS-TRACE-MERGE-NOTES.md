# Nexus Trace Merge Notes

Bu not, Gemini'nin `deanos/.gpt` yapisini diger alanlarla birlestirirken izleyecegi iz dusuncesi (trace) icin hazirlandi.

## Kopyalanan Kaynak
- Kaynak: `C:/Users/Deacjx/.gpt`
- Hedef: `C:/projects/deanos/.gpt`

## Merge Niyeti
- `.gpt` bagimsiz katman olarak korunur.
- `.claude` ve `.gemini` ile birlestirme sadece okuma/atif seviyesinde yapilir.
- Kopya alan, Gemini icin yerel ve hizli erisim noktasi olarak kullanilir.

## Gemini Icin Oncelik Sirasi
1. `deanos/.gpt/GPT.md`
2. `deanos/.gpt/manifest.yaml`
3. `deanos/.gpt/mcp.json`
4. `deanos/.agent-bridge/nexus-skill-map.json`
5. `deanos/guides/NEXUS-LAZY-SKILL-MCP-GUIDE.md`

## Trace Kurali
- Tool cagrisi varsa: ilgili tool map secimi
- `@rule/@guide/@skill` atifi varsa: sadece atiflanan dosyalar
- Tum klasor dump yok; lazy secim var

## Not
- Bu dosya chain-of-thought icermez.
- Operasyonel merge izi ve karar ozeti icerir.
