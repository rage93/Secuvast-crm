# [Django Material Dashboard PRO](https://app-generator.dev/product/material-dashboard-pro/django/)

**Django** starter styled with **[Material Dashboard PRO](https://app-generator.dev/product/material-dashboard-pro/django/)**, a premium `Bootstrap 5` KIT from [Creative-Tim](https://app-generator.dev/agency/creative-tim/). The product is designed to deliver the best possible user experience with highly customizable feature-rich pages. 

- 👉 [Django Material Dashboard PRO](https://app-generator.dev/product/material-dashboard-pro/django/) - `Product Page`
- 👉 [Django Material Dashboard PRO](https://django-material-dash2-pro.onrender.com/) - `LIVE Demo` 
- 👉 [Django Material Dashboard PRO](https://app-generator.dev/docs/products/django/material-dashboard-pro/index.html) - `Documentation` (learn how to use the product) 

<br />

## Features

- Simple, Easy-to-Extend Codebase
- [Material Dashboard](https://app-generator.dev/product/material-dashboard/) Design Integration
- Bootstrap Styling 
- DB Persistence: SQLite (default), can be used with MySql, PgSql
- Extended Users Profiles
- Authentication
   - Session-based 
   - OAuth GitHub, Google
- Apps:
  - [DEMO](https://django-material-dash2-pro.onrender.com/dynamic-dt/product/) **Dynamic DataTables** - generate server-side datatables without coding  
  - [DEMO](https://django-material-dash2-pro.onrender.com/api/product/) **Dynamic APIs** - Expose secure APIs without coding  
  - [DEMO](https://django-material-dash2-pro.onrender.com/charts/) **Charts** - powered by ApexCharts 
  - [DEMO](https://django-material-dash2-pro.onrender.com/react-charts) **React Integration**
  - **Media Files Manager** - empower users to manage and preview files with ease
  - **Celery** (async tasks)
- [Django CLI Package](https://app-generator.dev/docs/developer-tools/django-cli/index.html)
    - `Commit/rollback Git Changes`
    - `Backup & restore DB`
    - `Interact with Django Core`
    - `Manage Environment`
    - `Manage Dependencies`
- [Deployment](https://app-generator.dev/docs/deployment.html)
  - Docker/Docker Compose Scripts
  - CI/CD for [Render](https://app-generator.dev/docs/deployment/render/index.html)
- [Vite](https://app-generator.dev/docs/technologies/vite/index.html) for assets management

## Company Sign-Up


Only the first administrator should create an account using the company sign‑up page:

```
/company/signup/
```


During sign up the user account and the company are created in one step. After
registration you are redirected to the pricing page to select a plan and
complete payment via Stripe. Additional members are invited from the
administration area once signed in.


The full onboarding flow works as follows:

1. Visit the landing page and choose **Create Company**.
2. Fill out the sign‑up form which creates both the user and the company.
3. Pick a plan on the pricing page and complete payment when required.
4. After checkout you are taken straight to your company dashboard.
5. Invite additional members from the *Company → Users* section.

You can also start from the public pricing page. Choosing a plan there will
lead you to the sign‑up form with the plan preselected.


When running locally, add entries to your `hosts` file so subdomains resolve to
`127.0.0.1` (e.g. `myco.localhost`). After authentication, users are
automatically redirected to their company subdomain.


## Auto Reload with Docker

To develop locally with hot‑reload enabled, the Docker services mount the
project directory and run the application with reload flags. Start the stack
using:

```bash
docker compose up
```


The `appseed-app` container runs `python manage.py migrate` on startup so new
database tables are created automatically. If running the project outside of
Docker, remember to apply migrations manually with `python manage.py migrate`.


Whenever you modify the code, the web service reloads via Django's runserver
and the Celery worker restarts thanks to `watchmedo`.

## Data Integrity

Each `Company` row tracks a `row_version` that increments on every update. If
two sessions attempt to modify the same company concurrently, a validation
error prevents overwriting stale data.

When using PostgreSQL, row-level security restricts queries so that tenants can
only access their own records. The middleware sets the database parameter
`secuvast.current_company` for each request.

The admin change view now displays related audit logs so you can review changes
to a company at a glance. Superusers can switch between tenants via a new
dropdown in the admin header.

## Test Data

Default role permissions live in `fixtures/role_matrix.yml`. Sync them with:

```bash
python manage.py sync_roles
```

Run tests using `pytest`:

```bash
pytest
```

Admins can manage their subscription via Stripe's billing portal:

```bash
https://<company>.localhost/company/billing/
```

Generate demo data locally with:

```bash
python scripts/make_demo_data.py
```


## [Documentation](https://app-generator.dev/docs/products/django/material-dashboard-pro/index.html)

- Understand the codebase structure
- Prepare the environment
- Setting Up the Database
- Start the Project
- Switch from SQLite to MySql or PgSql
- Add a new model and migrate database
- Enable `Dynamic Tables` for a new model
- Enable `Dynamic API` for a new model
- Deploy on Render

![Django Material Dashboard PRO - Premium starter powered by Django and Bootstrap 5 - actively supported provided by App-Generator.](https://github.com/user-attachments/assets/6d45cb15-76e7-4b87-81bc-81ca71c96faf)

<br /> 

---
[Django Material Dashboard PRO](https://app-generator.dev/product/material-dashboard-pro/django/) - **Django** Starter provided by [App Generator](https://app-generator.dev)
