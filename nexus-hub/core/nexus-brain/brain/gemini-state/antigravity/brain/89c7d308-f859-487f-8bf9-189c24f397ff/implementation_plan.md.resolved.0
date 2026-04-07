# Fix Database Authentication for Local Development

The backend is failing to start because it cannot connect to the PostgreSQL database with the credentials provided for the "casaos" user. Based on previous logs, the backend was successfully running using SQLite.

## Proposed Changes

### [Backend](file:///c:/projects/github/EvATasks/backend)

#### [MODIFY] [.env](file:///c:/projects/github/EvATasks/backend/.env)

Comment out the `DATABASE_URL` that uses PostgreSQL and explicitly set `USE_POSTGRES=false` to use the local SQLite database. This is the safest way to get the backend running locally without modifying the PostgreSQL server itself.

```env
# Database - CasaOS Local PostgreSQL
# DATABASE_URL=postgresql://casaos:casaos@localhost:5432/casaos?sslmode=disable

# Legacy PostgreSQL config (if not using DATABASE_URL):
USE_POSTGRES=false
```

## Verification Plan

### Automated Tests
1. Run `npm run migrate` in the `backend` directory to ensure the SQLite database is initialized.
   - Command: `cd backend; npm run migrate`
2. Run `npm run dev` to verify the backend starts successfully.
   - Command: `cd backend; npm run dev`

### Manual Verification
- Check the terminal output for `✓ Database connected` and `✓ Server running on port 3000` (or 3001).
