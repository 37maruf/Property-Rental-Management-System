# RentEase – Property Rental & Management System

A Django project where **property owners** list properties and **tenants** search and send rental requests.

## Features
- Register / login / logout / update profile, with two roles: **Owner** and **Tenant**
- Owners: full CRUD on their own properties, view requests, accept / reject
- Tenants: browse, search & filter, send requests, cancel pending requests
- Search by location, property type, min / max rent (with pagination)
- Owner dashboard and tenant dashboard with request counts
- Reviews & ratings (1–5) after an accepted request, one review per tenant per property
- Custom middleware that guards `/owner/` and `/tenant/` pages by role
- Django Admin for Users, Properties, Rental Requests, Reviews
- Bonus: pagination, email notifications (printed in the terminal)

## Business rules
- Only logged-in tenants can send requests
- A tenant cannot request their own property
- Only the property owner can accept / reject
- No multiple pending requests for the same property (checked in form + DB constraint)
- Owners cannot edit or delete another owner's property (403)

## Setup
```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac / Linux

pip install -r requirements.txt
```

1. Create the PostgreSQL database:
   ```sql
   CREATE DATABASE property_management;
   ```
2. Copy `.env.example` to `.env` and fill in your values (secret key, DB password).
3. Run:
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py seed_demo      # optional demo data
   python manage.py runserver
   ```

Open http://127.0.0.1:8000/ and the admin at http://127.0.0.1:8000/admin/

Demo logins (after `seed_demo`): `demo_owner` / `demo_tenant`, password `demo12345`.

If `DB_NAME` is empty in `.env`, the project falls back to SQLite.

## Tests
```bash
python manage.py test
```

## Project structure
```
config/       settings, urls
accounts/     custom User (role), auth views, forms, middleware, decorators
properties/   Property model, CRUD, search & filter
rentals/      RentalRequest, Review, dashboards
templates/    Bootstrap 5 templates
```
