# IT Inventory V3 Technical Handoff

## Modern Infrastructure
- **Auth**: Microsoft Graph API (OAuth2) replaces legacy EWS.
- **Database**: PostgreSQL (v15+) replaces local SQLite.
- **Frontend**: Custom Glassmorphism CSS theme built on Vanilla CSS.

## Configuration (.env)
- `AZURE_CLIENT_ID`, `TENANT_ID`, `CLIENT_SECRET`: Graph API credentials.
- `EXCHANGE_EMAIL`: `support@findtalent.net`.
- `DATABASE_URL`: `postgresql://dean:Eralp123!@192.168.1.186:5432/inventory`.
- `APP_BASE_URL`: Public access URL for approval links.

## Core Modules
- `email_watcher.py`: Background job for email polling.
- `email_parser.py`: Regex-based personal data extractor.
- `notifier.py`: Teams / Email notification dispatcher.
- `graph_watcher.py`: Graph API specific implementation.

## Verification
- Clean database reset performed.
- Standard and Vertical table parsing verified.
- **Selin Yıldız** test (ID #28) confirmed successful end-to-end flow.
