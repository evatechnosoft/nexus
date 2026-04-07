# Domain-Based Routing and Multi-Language Implementation

The goal is to implement a multi-domain strategy for Evaitec:
1. **Inside Turkey**: Route users to `evaitec.com.tr` (Turkish content).
2. **Outside Turkey**: Route users to `evaitec.com` with language options (e.g., `/en`).
3. **Domain Redirects**: Auto-redirect `evaitec.com` to `evaitec.com.tr` if the user is in Turkey.

## User Review Required

> [!IMPORTANT]
> **Geo-Detection Strategy**: This plan assumes we can detect location via HTTP headers (e.g., `CF-IPCountry` from Cloudflare). If you are NOT using Cloudflare, please let me know, and I can switch to an IP database strategy (e.g., `geoip2`).
> **URL Structure**: We will use subpaths like `/en/` and `/tr/` or root based on domain.

## Proposed Changes

### Flask Backend (`src/app.py`)

#### [MODIFY] [app.py](file:///c:/projects/github/casatozima/src/app.py)
1. Add a `before_request` hook or middleware to handle:
   - Detecting the `Host` header.
   - Checking for `CF-IPCountry` (Cloudflare) or fallback to detection.
   - Redirecting logic based on host + location.
2. Implement a simple localization helper that loads translations from a JSON file.
3. Update routes to handle language prefixes or detect language from the session/domain.

### Localization (`src/translations/`)

#### [NEW] [tr.json](file:///c:/projects/github/casatozima/src/translations/tr.json)
#### [NEW] [en.json](file:///c:/projects/github/casatozima/src/translations/en.json)
- Store all UI strings in these files.

### Frontend (`src/templates/`)

#### [MODIFY] [index.html](file:///c:/projects/github/casatozima/src/templates/index.html)
- Replace hardcoded text with template variables (e.g., `{{ lang.title }}`).
- Add a language switcher if needed (though the user prefers domain-based).

## Verification Plan

### Automated Tests
- Mock `Host` and `CF-IPCountry` headers in Flask tests to verify redirection.
- Verify that accessing `evaitec.com` with `CF-IPCountry: TR` redirects to `evaitec.com.tr`.

### Manual Verification
- Test with different domains (if possible in local `/etc/hosts`).
- Verify English content is served correctly on `evaitec.com`.
