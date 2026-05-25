# EDUNOVA Flask Web App

EDUNOVA is a student career, education, scholarship, school discovery, and mentorship guidance platform designed to help students from high school through university make better academic and career decisions.

The platform helps students create profiles, share their academic background, explore opportunities, save scholarships, and request guidance from experts and alumni.
## Live Demo

Access EDUNOVA here:

https://edunova-ixpb.onrender.com/
## Features

- Multi-page Flask web application
- Student account creation and login
- Student dashboard
- Academic background and career profile
- Career prospects and study destination tracking
- Scholarship and opportunity listings
- School and program discovery
- Save and unsave opportunities
- Mentorship request system
- Admin dashboard for managing students and mentorship requests
- SQLite database for local development
- HTML templates, CSS styling, and JavaScript interactions

## Tech Stack

- Python
- Flask
- SQLite
- HTML
- CSS
- JavaScript
- Werkzeug security for password hashing

## Project Structure

```text
edunova_webapp/
  app.py
  requirements.txt
  README.md
  templates/
  static/
  .gitignore
```

## Run Locally

Clone the repository:

```bash
git clone https://github.com/Jordanfonoscholar237/Edunova.git

```

Go into the project folder:

```bash
cd Edunova
```

Create a virtual environment:

```bash
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

Run the app:

```bash
python app.py
```

Open in your browser:

```text
http://127.0.0.1:5000
```

## Admin Access

Admin access is controlled through the `EDUNOVA_ADMIN_EMAIL` environment variable.

For local development, set the admin email before running the application if you want to change the default admin account.

## Environment Variables

For production, set:

```text
EDUNOVA_SECRET_KEY=your-secure-secret-key
EDUNOVA_ADMIN_EMAIL=your-admin-email@example.com
```

Do not upload private `.env` files, secret keys, database files, or student data to GitHub.

## Deployment Notes

Before public launch:

- Use a strong `EDUNOVA_SECRET_KEY`
- Use PostgreSQL instead of SQLite for real student data
- Enable HTTPS
- Add email verification
- Add password reset
- Protect student personal data
- Deploy using Render, Railway, PythonAnywhere, or a VPS

For deployment, add Gunicorn to `requirements.txt`:

```text
gunicorn==22.0.0
```

Example production start command:

```bash
gunicorn app:app
```

## Contact

Email:

```text
jordanfonoscholar237@gmail.com
```

WhatsApp:

```text
+237 693 914 501
+237 676 603 724
```
