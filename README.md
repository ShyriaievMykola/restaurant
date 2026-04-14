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
