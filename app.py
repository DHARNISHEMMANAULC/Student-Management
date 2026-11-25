import os
import sqlite3
from flask import (
    Flask, render_template, request,
    redirect, url_for, flash, jsonify, g
)

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY", "mevi-workshop-development-key"
)

# Database configuration
os.makedirs(app.instance_path, exist_ok=True)

DATABASE = os.environ.get(
    "DATABASE_PATH",
    os.path.join(app.instance_path, "management.db")
)


def get_db():
    """Open one SQLite connection for the current request."""
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Create the students table if it does not already exist."""
    db = get_db()
    db.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            phone TEXT NOT NULL,
            course TEXT NOT NULL,
            year TEXT NOT NULL,
            gender TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    db.commit()


@app.before_request
def ensure_database():
    init_db()


@app.route("/")
def index():
    db = get_db()
    students = db.execute(
        "SELECT * FROM students ORDER BY id DESC"
    ).fetchall()

    total_students = db.execute(
        "SELECT COUNT(*) FROM students"
    ).fetchone()[0]

    course_count = db.execute(
        "SELECT COUNT(DISTINCT course) FROM students"
    ).fetchone()[0]

    course_stats = db.execute("""
        SELECT course, COUNT(*) AS total
        FROM students
        GROUP BY course
        ORDER BY total DESC, course
    """).fetchall()

    return render_template(
        "index.html",
        students=students,
        total_students=total_students,
        course_count=course_count,
        course_stats=course_stats
    )


@app.route("/add", methods=["POST"])
def add_student():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    phone = request.form.get("phone", "").strip()
    course = request.form.get("course", "").strip()
    year = request.form.get("year", "").strip()
    gender = request.form.get("gender", "").strip()

    if not all([name, email, phone, course, year, gender]):
        flash("Please complete all student fields.", "error")
        return redirect(url_for("index") + "#registration")

    if not phone.isdigit() or len(phone) != 10:
        flash("Enter a valid 10-digit phone number.", "error")
        return redirect(url_for("index") + "#registration")

    try:
        db = get_db()
        db.execute("""
            INSERT INTO students
            (name, email, phone, course, year, gender)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, email, phone, course, year, gender))
        db.commit()
        flash("Student registered successfully.", "success")
    except sqlite3.IntegrityError:
        flash("That email address is already registered.", "error")

    return redirect(url_for("index") + "#records")


@app.route("/edit/<int:student_id>", methods=["POST"])
def edit_student(student_id):
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    phone = request.form.get("phone", "").strip()
    course = request.form.get("course", "").strip()
    year = request.form.get("year", "").strip()
    gender = request.form.get("gender", "").strip()

    if not all([name, email, phone, course, year, gender]):
        flash("Please complete all student fields.", "error")
        return redirect(url_for("index") + "#records")

    if not phone.isdigit() or len(phone) != 10:
        flash("Enter a valid 10-digit phone number.", "error")
        return redirect(url_for("index") + "#records")

    try:
        db = get_db()
        cursor = db.execute("""
            UPDATE students
            SET name = ?, email = ?, phone = ?, course = ?,
                year = ?, gender = ?
            WHERE id = ?
        """, (name, email, phone, course, year, gender, student_id))
        db.commit()

        if cursor.rowcount:
            flash("Student details updated.", "success")
        else:
            flash("Student record was not found.", "error")
    except sqlite3.IntegrityError:
        flash("Another student is already using that email.", "error")

    return redirect(url_for("index") + "#records")


@app.route("/delete/<int:student_id>", methods=["POST"])
def delete_student(student_id):
    db = get_db()
    db.execute("DELETE FROM students WHERE id = ?", (student_id,))
    db.commit()
    flash("Student record deleted.", "success")
    return redirect(url_for("index") + "#records")


@app.route("/api/students")
def students_api():
    """Return student records as JSON."""
    rows = get_db().execute(
        "SELECT * FROM students ORDER BY id DESC"
    ).fetchall()
    return jsonify([dict(row) for row in rows])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
