# Agent Bridge (ai + claude + gemini)

Bu dizin, C:\Users\Deacjx altindaki uc farkli ajan hafiza/kurallarini tek bir giris noktasinda toplamak icin olusturuldu.

## Kaynaklar
- AI memory: `C:/Users/Deacjx/.ai/memory`
- Claude rules: `C:/Users/Deacjx/.claude/rules`
- Gemini state: `C:/Users/Deacjx/.gemini`
- MCP base config: `C:/Users/Deacjx/.mcp.json`

## Dosyalar
- `mcp-bridge.json`: MCP tarafinda tek bir filesystem server ile 3 kaynagi birden mount eden hazir config.
- `source-map.json`: Hangi klasor ne amacla kullaniliyor bilgisini verir.

## Hedef Kullanim
1. `scripts/setup-agent-bridge.ps1` calistirilir.
2. Script, aktif MCP ayarlarina zarar vermeden bridge config'i kopyalar.
3. MCP istemcisi bu config ile acildiginda uc kaynaga tek MCP server uzerinden erisir.

## Not
Bu yapi kopyalama yapmaz; kaynak klasorleri oldugu yerde kullanir.
