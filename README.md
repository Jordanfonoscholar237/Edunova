# EDUNOVA Flask Web App

A complete multi-page web app for student career orientation, educational orientation, scholarships, schools, and mentorship.

## What is included

- Python Flask backend
- SQLite database
- HTML templates
- CSS styling
- JavaScript interactions
- Multi-page navigation
- Student account creation and login
- Student dashboard
- Profile completion tracking
- Academic background and career prospects
- Opportunity search and filters
- Save / unsave opportunities
- Mentorship request system
- Admin page to view students and mentorship requests

## Run locally

```bash
cd edunova_webapp
python -m venv .venv
```

Activate the virtual environment.

Windows:

```bash
.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run:

```bash
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

## Admin

Create an account using:

```text
jordanfonoscholar237@gmail.com
```

Then visit:

```text
http://127.0.0.1:5000/admin
```

To change the admin email, set `EDUNOVA_ADMIN_EMAIL`.

## Production notes

Before public launch, use PostgreSQL, set a strong `EDUNOVA_SECRET_KEY`, enable HTTPS, add email verification, and deploy to Render, Railway, PythonAnywhere, or a VPS.
