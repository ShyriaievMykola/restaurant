## Restaurant Menu (Django)

Simple restaurant menu app with:
- category and tag based filtering
- list and detail pages
- JSON API endpoint
- autocomplete endpoint

## Requirements

- Python 3.10+
- pip

## Local Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Environment Variables

Create `.env` (you can copy from `.env.example`):

```env
DJANGO_SECRET_KEY=replace-with-your-secret-key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost,0.0.0.0
DJANGO_CSRF_TRUSTED_ORIGINS=http://127.0.0.1:8000,http://localhost:8000
```

For production (HTTPS + domain), set trusted origins with scheme, for example:

```env
DJANGO_ALLOWED_HOSTS=example.com,www.example.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://example.com,https://www.example.com
```

## Run Migrations

```bash
python manage.py migrate
```

## Seed Demo Data

```bash
python manage.py seed_menu
```

Optional full reset before seeding:

```bash
python manage.py seed_menu --clear
```

## Run Server

```bash
python manage.py runserver
```

## Run Tests

```bash
python manage.py test
```

## Docker

```bash
docker-compose up --build
```

## Heroku CD (separate from existing CD)

The repository now supports an additional Heroku deployment workflow in `.github/workflows/cd-heroku.yml`.
It does not replace your current CD pipeline and can run in parallel.

### What this workflow does

1. `build` job: installs dependencies and runs Django tests.
2. `deploy` job: deploys the app to Heroku only if the build job succeeds.

Triggers:
- push to `main`
- push to `master`
- pull request to `main` or `master` (tests only)
- manual run via `workflow_dispatch`

Merge-to-master condition:
- On push to `main`, successful `Build and test` automatically merges `main` into `master`.
- Heroku deploy runs only on `push`, so PR checks do not trigger deployment.

### Required GitHub Secrets

Add these in repository Settings -> Secrets and variables -> Actions:

- `HEROKU_API_KEY` (Heroku account API key)
- `HEROKU_EMAIL` (email of Heroku account owner)
- `HEROKU_APP_NAME` (target Heroku app name)
- `DJANGO_SECRET_KEY` (production Django secret key)

### Optional GitHub Variables

- `DJANGO_ALLOWED_HOSTS`
- `DJANGO_CSRF_TRUSTED_ORIGINS`

If optional variables are not set, workflow defaults are used:
- `DJANGO_ALLOWED_HOSTS=<HEROKU_APP_NAME>.herokuapp.com`
- `DJANGO_CSRF_TRUSTED_ORIGINS=https://<HEROKU_APP_NAME>.herokuapp.com`

### Connect GitHub and Heroku

1. Create a Heroku app.
2. Open Account Settings in Heroku and copy API key.
3. Save secrets listed above in GitHub repository settings.
4. Push a commit to `main` or `master`.
5. Verify successful run in GitHub Actions.
