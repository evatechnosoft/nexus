# User Authentication Implementation Plan

Add JWT-based authentication to the Flask API to secure endpoints and manage user sessions.

## Proposed Changes

### Backend (Flask)

#### [MODIFY] [requirements.txt](file:///c:/projects/github/casatozima/requirements.txt)
- Add `flask-jwt-extended`
- Add `flask-bcrypt` (optional, as Werkzeug can handle hashing, but bcrypt is more robust)

#### [MODIFY] [app.py](file:///c:/projects/github/casatozima/src/app.py)
- Update `User` model: add `password_hash = db.Column(db.String(128), nullable=False)`.
- Import `JWTManager`, `create_access_token`, `jwt_required`, `get_jwt_identity`.
- Initialize `JWTManager(app)` and set `JWT_SECRET_KEY`.
- Add `/api/auth/register` (creates user with hashed password).
- Add `/api/auth/login` (verifies password and returns token).
- Secure `/api/users` endpoints with `@jwt_required()`.

---

### Dashboard (Frontend)

#### [MODIFY] [index.html](file:///c:/projects/github/casatozima/src/templates/index.html)
- Add Login/Logout UI elements.
- Update fetch calls to include JWT token in headers.

## Verification Plan

### Automated Tests
- Create a test script `tests/test_auth.py` to:
    - Register a new user.
    - Login and receive a JWT.
    - Access protected endpoints with and without the JWT.

### Manual Verification
- Deploy to `flask-dev` and verify the login flow via the dashboard.
- Use Postman or `curl` to test the API endpoints.
