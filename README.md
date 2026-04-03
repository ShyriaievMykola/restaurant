# restaurant

Restaurant website on Django with hierarchical categories and advanced menu filters.

## Features

- Two-level category structure (category and subcategory)
- Filters by search query, category, tags, price range, and availability
- Tag filter modes: match any selected tag (OR) or match all selected tags (AND)
- Sorting by name, price, popularity, and newest
- Active filter chips with one-click removal
- Pagination on menu list page
- Quick menu stats: total, in-stock, unavailable, average price
- JSON API for filtered menu items: `/api/items/`
- Django admin management for categories, tags, and menu items

## Run Locally

1. Create environment file:

   ```powershell
   Copy-Item .env.example .env
   ```

2. Activate environment:

	```powershell
	.\.venv\Scripts\Activate.ps1
	```

3. Apply migrations:

	```powershell
	manage.py migrate
	```

4. Seed demo menu data:

	```powershell
	manage.py seed_menu
	```

5. Start server:

	```powershell
	manage.py runserver 0.0.0.0:8000
	```

## Docker Run

1. Create environment file:

   ```powershell
   Copy-Item .env.example .env
   ```

2. Build and start:

   ```powershell
   docker compose up --build
   ```

The web container runs migrations before starting the app.

## GitHub CI/CD with Local Runner

1. Create a self-hosted runner in repository settings:

	- Settings -> Actions -> Runners -> New self-hosted runner
	- Install it on your local machine with Docker installed
	- Add label `local-deploy` to that runner

2. Add repository secret:

	- `DJANGO_SECRET_KEY`

3. Optional repository variables:

	- `DJANGO_DEBUG` (default: `False`)
	- `DJANGO_ALLOWED_HOSTS` (default: `127.0.0.1,localhost,0.0.0.0`)

4. Push to `main` or `master`.

Workflow split:

- CI in [.github/workflows/ci.yml](.github/workflows/ci.yml): full tests and docker-based tests.
- CD in [.github/workflows/cd.yml](.github/workflows/cd.yml): deploy on self-hosted `local-deploy` runner after successful CI.

## Run Tests

```powershell
    manage.py test
```