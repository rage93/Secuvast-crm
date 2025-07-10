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


Only authenticated users can create a company. First register an account and then visit the company sign‑up page:

```
/company/signup/
```


During company creation only the organization details are collected. Your user
account is linked as the company admin and you are redirected straight to the
dashboard. Choose a **Basic** or **Pro** subscription from the pricing page when
you're ready to activate the company via Stripe. The company becomes active once
the payment is verified or after manual confirmation by an administrator. Each
successful checkout stores the Stripe subscription ID on the Company so the
status can be validated later.


The full onboarding flow works as follows:

1. Register a user account from the login page.
2. After signing in, choose **Create Company** from the navigation.
3. Enter your company details.
4. After saving the company you are redirected to the dashboard and a short
   message confirms the organization was created.
5. Visit the pricing page whenever you wish to activate the company by choosing
   the Basic or Pro plan and completing payment via Stripe.
6. Once payment is confirmed you can invite teammates from the **Invite User**
   option under the Users menu or create accounts directly with **New User**.

You can also start from the public pricing page. Choosing a plan there will
lead you to the sign‑up form with the plan preselected.


All companies share the same base URL. Access to data is restricted based on

the company associated with each user. Make sure you access the site using the
domain configured in `SAAS_ROOT_DOMAIN` (default `localhost`). If you still
visit old subdomains, the application now redirects them back to the base
domain so your session cookies work correctly.

After pulling updates remember to apply migrations:

```bash
python manage.py migrate



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

## Email Verification

User registration now sends a confirmation email using `django-allauth`.
Set your Gmail credentials in the `.env` file:

```
EMAIL_HOST=<your gmail address>
EMAIL_PASS=<your app password>
DEFAULT_FROM_EMAIL=<display sender>
```

With these variables defined the application sends a verification link to
new users. Accounts remain inactive until the email address is confirmed.

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

## Link Checker

Ensure navigation links work for each user role using the
`check_links` management command. It logs in as the specified user,
crawls pages starting from `/`, and reports any HTTP errors.

```bash
python manage.py check_links --username=admin
```

Use `--depth` to follow links recursively or `--start-url` to test a
different entry point.

This command is also available via the **Tasks** page in the admin
sidebar. Choose the `check_links.py` script and Celery will execute it
asynchronously, storing the logs for later review.


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
