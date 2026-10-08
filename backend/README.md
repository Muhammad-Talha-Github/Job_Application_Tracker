# Backend setup

1. Create a PostgreSQL database named `job_tracker` (for example, with pgAdmin or `createdb -U postgres job_tracker`).
2. Copy `.env.example` to `.env`. Set `DATABASE_URL` and replace `JWT_SECRET_KEY` with a random secret at least 32 characters long.
3. From this `backend` directory, install packages and apply migrations:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   alembic upgrade head
   ```

4. Start the API with `uvicorn app.main:app --reload`.
5. Run the backend tests with `python -m pytest -q`.

## Existing application data

Migration `0002_user_ownership` adds the users table and an ownership foreign key without dropping application rows. Before applying it to a database that already has applications, set `LEGACY_OWNER_EMAIL` and `LEGACY_OWNER_PASSWORD` in the ignored `.env`. The migration hashes that password with Argon2, creates the designated owner account, links every existing application to it, then makes `user_id` required. Remove those two one-time values from `.env` after the migration succeeds. A database with no existing application rows does not need the legacy-owner settings.

## Authentication

- `POST /auth/register` creates an account with an Argon2 password hash.
- `POST /auth/login` returns a short-lived JWT. Send it as `Authorization: Bearer <token>` to use `/applications`.
- The API looks up the token's user and filters all application queries by that user's ID. The request body never chooses the owner.
- Alembic records applied revisions in `alembic_version`. When a model changes later, review a generated migration with `alembic revision --autogenerate -m "describe the change"`, then apply it with `alembic upgrade head`.

Each API request gets a short-lived SQLAlchemy session, which is closed after the request. PostgreSQL stores committed data across FastAPI and frontend restarts.
