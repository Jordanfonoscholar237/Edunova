from __future__ import annotations

import os
import sqlite3
from datetime import datetime
from functools import wraps
from pathlib import Path

from flask import Flask, flash, g, jsonify, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "data" / "edunova.db"

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("EDUNOVA_SECRET_KEY", "change-this-secret-key-before-launch")
app.config["ADMIN_EMAIL"] = os.environ.get("EDUNOVA_ADMIN_EMAIL", "jordanfonoscholar237@gmail.com").lower()


def get_db():
    if "db" not in g:
        DATABASE.parent.mkdir(exist_ok=True)
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def one(sql, params=()):
    return get_db().execute(sql, params).fetchone()


def all_rows(sql, params=()):
    return get_db().execute(sql, params).fetchall()


def run(sql, params=()):
    db = get_db()
    db.execute(sql, params)
    db.commit()


def init_db():
    db = get_db()
    db.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        whatsapp TEXT,
        city TEXT,
        country TEXT,
        language TEXT,
        current_level TEXT,
        school TEXT,
        field_of_study TEXT,
        latest_results TEXT,
        strong_subjects TEXT,
        career_interest TEXT,
        preferred_destination TEXT,
        goals TEXT,
        created_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS opportunities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        type TEXT NOT NULL,
        region TEXT NOT NULL,
        level TEXT NOT NULL,
        field TEXT NOT NULL,
        deadline TEXT NOT NULL,
        description TEXT NOT NULL,
        requirements TEXT,
        link TEXT,
        created_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS saved_opportunities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        opportunity_id INTEGER NOT NULL,
        created_at TEXT NOT NULL,
        UNIQUE(user_id, opportunity_id)
    );

    CREATE TABLE IF NOT EXISTS mentorship_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        field TEXT NOT NULL,
        mentor_type TEXT NOT NULL,
        message TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'Pending',
        created_at TEXT NOT NULL
    );
    """)
    db.commit()
    seed_opportunities()


def seed_opportunities():
    total = one("SELECT COUNT(*) AS total FROM opportunities")["total"]
    if total:
        return
    now = datetime.utcnow().isoformat()
    items = [
        ("Cameroon Excellence Study Support", "Scholarship", "Cameroon", "High School / Undergraduate", "All fields", "Rolling", "Support and orientation for strong students seeking local scholarship opportunities and application guidance.", "Good academic record, motivation, and complete EDUNOVA profile.", ""),
        ("International Undergraduate Scholarship Pathway", "Scholarship", "Europe", "Upper Sixth / Graduate", "Science, Business, Arts, Technology", "Varies by university", "Guidance for students preparing applications to universities abroad with partial or full scholarship possibilities.", "Strong academic record, language readiness, passport, essays, and recommendation letters.", ""),
        ("STEM Future Leaders Opportunity", "Scholarship", "United States / Canada", "Upper Sixth / Undergraduate", "Science, Technology, Engineering, Mathematics", "Annual", "Recommended for students interested in engineering, computer science, health sciences, data, and innovation.", "Strong STEM subjects, projects, leadership, and English readiness.", ""),
        ("Cameroon University Program Finder", "School", "Cameroon", "Form 5 / Upper Sixth / Undergraduate", "All fields", "Admission season", "Compare local universities and programs based on your interests, level, language, and career goals.", "Open to students exploring local higher education options.", ""),
        ("Francophone and Bilingual Study Options", "School", "Africa", "High School / Undergraduate", "All fields", "Varies", "Explore bilingual and French-speaking institutions in Cameroon and other African countries.", "French or bilingual study interest.", ""),
        ("Alumni Abroad Mentorship Circle", "Mentorship", "Online", "All levels", "All fields", "Monthly", "Meet alumni currently abroad and learn about admission, scholarships, student life, and career preparation.", "Complete profile and submit mentorship request.", ""),
        ("Career Expert Guidance Session", "Mentorship", "Online", "High School / University", "Medicine, Law, Business, Technology, Engineering", "Monthly", "Ask real experts questions about the careers you are considering before choosing a path.", "Clear career interest and questions for the mentor.", ""),
        ("Student Skills and Internship Readiness", "Internship", "Cameroon", "Undergraduate / Graduate", "Business, Technology, Communication, NGOs", "Rolling", "Prepare your CV, LinkedIn, portfolio, and application documents for internships and youth opportunities.", "University student or graduate ready to build professional skills.", ""),
        ("EDUNOVA Orientation Webinar", "Event", "Online", "All levels", "All fields", "Next session", "A live online session on career orientation, scholarships, choosing schools, and preparing applications.", "Open to students, parents, and school partners.", ""),
        ("Asia Study Preparation Track", "Scholarship", "Asia", "Upper Sixth / Undergraduate / Graduate", "Engineering, Medicine, Business, Technology", "Varies", "Guidance for students considering China, Japan, South Korea, India, and other Asian study destinations.", "Academic readiness, passport planning, and study destination interest.", ""),
    ]
    for item in items:
        run("""INSERT INTO opportunities
        (title, type, region, level, field, deadline, description, requirements, link, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (*item, now))


def current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    return one("SELECT * FROM users WHERE id = ?", (user_id,))


@app.context_processor
def inject_user():
    user = current_user()
    return {
        "current_user": user,
        "is_admin": bool(user and user["email"].lower() == app.config["ADMIN_EMAIL"]),
        "admin_email": app.config["ADMIN_EMAIL"],
    }


def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not current_user():
            flash("Please login to continue.", "error")
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)
    return wrapper


def admin_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        user = current_user()
        if not user or user["email"].lower() != app.config["ADMIN_EMAIL"]:
            flash("Admin access required.", "error")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapper


def profile_completion(user):
    fields = ["full_name", "email", "whatsapp", "city", "country", "language", "current_level", "school", "field_of_study", "latest_results", "strong_subjects", "career_interest", "preferred_destination", "goals"]
    filled = sum(1 for field in fields if user[field] and str(user[field]).strip())
    return round((filled / len(fields)) * 100)


def saved_ids(user_id):
    rows = all_rows("SELECT opportunity_id FROM saved_opportunities WHERE user_id = ?", (user_id,))
    return {row["opportunity_id"] for row in rows}


def match_opportunities(user, limit=None):
    items = all_rows("SELECT * FROM opportunities ORDER BY created_at DESC")
    keywords = " ".join([
        user["field_of_study"] or "",
        user["career_interest"] or "",
        user["preferred_destination"] or "",
        user["current_level"] or "",
        user["strong_subjects"] or "",
    ]).lower().split()
    scored = []
    for item in items:
        haystack = " ".join([item["title"], item["type"], item["region"], item["level"], item["field"], item["description"]]).lower()
        score = 0
        if user["preferred_destination"] and user["preferred_destination"].lower() in item["region"].lower():
            score += 5
        if item["field"].lower() == "all fields":
            score += 2
        for word in keywords:
            if len(word) > 3 and word in haystack:
                score += 1
        if score > 0:
            scored.append((score, item))
    scored.sort(key=lambda x: x[0], reverse=True)
    result = [item for _, item in scored]
    return result[:limit] if limit else result


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/services")
def services():
    return render_template("services.html")


@app.route("/opportunities")
def opportunities():
    q = request.args.get("q", "").strip()
    type_filter = request.args.get("type", "").strip()
    region = request.args.get("region", "").strip()

    sql = "SELECT * FROM opportunities WHERE 1=1"
    params = []
    if q:
        sql += " AND (title LIKE ? OR description LIKE ? OR field LIKE ?)"
        params.extend([f"%{q}%", f"%{q}%", f"%{q}%"])
    if type_filter:
        sql += " AND type = ?"
        params.append(type_filter)
    if region:
        sql += " AND region = ?"
        params.append(region)
    sql += " ORDER BY created_at DESC"
    items = all_rows(sql, tuple(params))
    saved = saved_ids(current_user()["id"]) if current_user() else set()
    return render_template("opportunities.html", opportunities=items, saved=saved, q=q, type_filter=type_filter, region=region)


@app.route("/scholarships")
def scholarships():
    items = all_rows("SELECT * FROM opportunities WHERE type = 'Scholarship' ORDER BY created_at DESC")
    saved = saved_ids(current_user()["id"]) if current_user() else set()
    return render_template("opportunities.html", opportunities=items, saved=saved, q="", type_filter="Scholarship", region="", page_title="Scholarships")


@app.route("/schools")
def schools():
    items = all_rows("SELECT * FROM opportunities WHERE type = 'School' ORDER BY created_at DESC")
    saved = saved_ids(current_user()["id"]) if current_user() else set()
    return render_template("opportunities.html", opportunities=items, saved=saved, q="", type_filter="School", region="", page_title="Schools and Programs")


@app.route("/opportunities/<int:opportunity_id>")
def opportunity_detail(opportunity_id):
    item = one("SELECT * FROM opportunities WHERE id = ?", (opportunity_id,))
    if not item:
        return render_template("404.html"), 404
    saved = bool(current_user() and item["id"] in saved_ids(current_user()["id"]))
    return render_template("opportunity_detail.html", item=item, saved=saved)


@app.route("/opportunities/<int:opportunity_id>/save", methods=["POST"])
@login_required
def save_opportunity(opportunity_id):
    user = current_user()
    existing = one("SELECT id FROM saved_opportunities WHERE user_id = ? AND opportunity_id = ?", (user["id"], opportunity_id))
    if existing:
        run("DELETE FROM saved_opportunities WHERE id = ?", (existing["id"],))
        flash("Opportunity removed from saved items.", "success")
    else:
        run("INSERT OR IGNORE INTO saved_opportunities (user_id, opportunity_id, created_at) VALUES (?, ?, ?)", (user["id"], opportunity_id, datetime.utcnow().isoformat()))
        flash("Opportunity saved.", "success")
    return redirect(request.referrer or url_for("opportunities"))


@app.route("/mentorship", methods=["GET", "POST"])
def mentorship():
    if request.method == "POST":
        if not current_user():
            flash("Create an account or login before requesting mentorship.", "error")
            return redirect(url_for("login"))
        field = request.form.get("field", "").strip()
        mentor_type = request.form.get("mentor_type", "").strip()
        message = request.form.get("message", "").strip()
        if not field or not mentor_type or not message:
            flash("Please complete all mentorship request fields.", "error")
        else:
            run("INSERT INTO mentorship_requests (user_id, field, mentor_type, message, status, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                (current_user()["id"], field, mentor_type, message, "Pending", datetime.utcnow().isoformat()))
            flash("Mentorship request submitted. EDUNOVA will contact you.", "success")
            return redirect(url_for("dashboard"))
    return render_template("mentorship.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        full_name = request.form.get("full_name", "").strip()
        if not full_name or not email or not password:
            flash("Full name, email, and password are required.", "error")
            return redirect(url_for("register"))
        if one("SELECT id FROM users WHERE email = ?", (email,)):
            flash("An account with this email already exists. Please login.", "error")
            return redirect(url_for("login"))
        run("""INSERT INTO users
        (full_name, email, password_hash, whatsapp, city, country, language, current_level, school, field_of_study, latest_results, strong_subjects, career_interest, preferred_destination, goals, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                full_name, email, generate_password_hash(password),
                request.form.get("whatsapp", "").strip(),
                request.form.get("city", "").strip(),
                request.form.get("country", "").strip(),
                request.form.get("language", "").strip(),
                request.form.get("current_level", "").strip(),
                request.form.get("school", "").strip(),
                request.form.get("field_of_study", "").strip(),
                request.form.get("latest_results", "").strip(),
                request.form.get("strong_subjects", "").strip(),
                request.form.get("career_interest", "").strip(),
                request.form.get("preferred_destination", "").strip(),
                request.form.get("goals", "").strip(),
                datetime.utcnow().isoformat(),
            ))
        user = one("SELECT * FROM users WHERE email = ?", (email,))
        session.clear()
        session["user_id"] = user["id"]
        flash("Account created successfully. Welcome to EDUNOVA.", "success")
        return redirect(url_for("dashboard"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = one("SELECT * FROM users WHERE email = ?", (email,))
        if not user or not check_password_hash(user["password_hash"], password):
            flash("Invalid email or password.", "error")
            return redirect(url_for("login"))
        session.clear()
        session["user_id"] = user["id"]
        flash("Welcome back.", "success")
        return redirect(request.args.get("next") or url_for("dashboard"))
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("home"))


@app.route("/dashboard")
@login_required
def dashboard():
    user = current_user()
    matches = match_opportunities(user, limit=6)
    saved_items = all_rows("""SELECT opportunities.* FROM opportunities
        JOIN saved_opportunities ON saved_opportunities.opportunity_id = opportunities.id
        WHERE saved_opportunities.user_id = ?
        ORDER BY saved_opportunities.created_at DESC""", (user["id"],))
    requests = all_rows("SELECT * FROM mentorship_requests WHERE user_id = ? ORDER BY created_at DESC", (user["id"],))
    return render_template("dashboard.html", user=user, completion=profile_completion(user), matches=matches, saved_items=saved_items, requests=requests)


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    user = current_user()
    if request.method == "POST":
        run("""UPDATE users SET full_name=?, whatsapp=?, city=?, country=?, language=?, current_level=?, school=?, field_of_study=?, latest_results=?, strong_subjects=?, career_interest=?, preferred_destination=?, goals=? WHERE id=?""",
            (
                request.form.get("full_name", "").strip(),
                request.form.get("whatsapp", "").strip(),
                request.form.get("city", "").strip(),
                request.form.get("country", "").strip(),
                request.form.get("language", "").strip(),
                request.form.get("current_level", "").strip(),
                request.form.get("school", "").strip(),
                request.form.get("field_of_study", "").strip(),
                request.form.get("latest_results", "").strip(),
                request.form.get("strong_subjects", "").strip(),
                request.form.get("career_interest", "").strip(),
                request.form.get("preferred_destination", "").strip(),
                request.form.get("goals", "").strip(),
                user["id"],
            ))
        flash("Profile updated successfully.", "success")
        return redirect(url_for("dashboard"))
    return render_template("profile.html", user=user)


@app.route("/admin")
@admin_required
def admin():
    students = all_rows("SELECT * FROM users ORDER BY created_at DESC")
    requests = all_rows("""SELECT mentorship_requests.*, users.full_name, users.email, users.whatsapp
        FROM mentorship_requests JOIN users ON users.id = mentorship_requests.user_id
        ORDER BY mentorship_requests.created_at DESC""")
    return render_template("admin.html", students=students, requests=requests)


@app.route("/api/opportunities")
def api_opportunities():
    rows = all_rows("SELECT * FROM opportunities ORDER BY created_at DESC")
    return jsonify([dict(row) for row in rows])


@app.errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404


with app.app_context():
    init_db()


if __name__ == "__main__":
    app.run(debug=True)
