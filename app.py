
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.secret_key = "your_secret_key"
db = SQLAlchemy(app)

# Student model with user_id and password_hash
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    age = db.Column(db.Integer)
    branch = db.Column(db.String(100))
    highest_qualification = db.Column(db.String(100))
    graduation_year = db.Column(db.Integer)
    program = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.String(100), unique=True)
    password_hash = db.Column(db.String(200))

    

    def __repr__(self):
        return f'<Student {self.name}>'

# Ensure tables are created
with app.app_context():
    db.create_all()

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form.get("email")
        phone = request.form.get("phone")

        # Redirecting user to the registration page
        return redirect(url_for("register", email = email, phone=phone))

    return render_template("signup.html")


# Home/Register Route
@app.route("/register", methods=["GET", "POST"])
def register():
    email = request.args.get("email", "")  # Get email from query parameters (default empty if not found)
    phone = request.args.get("phone", "")

    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        age = request.form.get("age")
        branch = request.form.get("branch")
        highest_qualification = request.form.get("highest_qualification")
        graduation_year = request.form.get("graduation_year")
        program = request.form.get("program")
        user_id = request.form.get("user_id")
        password = request.form.get("password")

        # Basic validations
        if not all([name, email, phone, age, branch, highest_qualification, graduation_year, program, user_id, password]):
            flash("Please fill in all fields.", "error")
            return redirect(url_for("register"))

        if Student.query.filter_by(email=email).first():
            flash("Email already registered.", "error")
            return redirect(url_for("register"))

        if Student.query.filter_by(user_id=user_id).first():
            flash("User ID already taken. Choose another.", "error")
            return redirect(url_for("register"))
        password= request.form.get("password")
        password_hash = generate_password_hash(password)

        new_student = Student(
            name=name,
            email=email,
            phone=phone,
            age=int(age),
            branch=branch,
            highest_qualification=highest_qualification,
            graduation_year=int(graduation_year),
            program=program,
            user_id=user_id,
            password_hash=password_hash
        )

        db.session.add(new_student)
        db.session.commit()

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html",email=email, phone=phone)

# Student Login Route
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user_id = request.form.get("user_id")
        password = request.form.get("password")

        # Check if student exists in the database
        student = Student.query.filter_by(user_id=user_id).first()
        if student:
            print(f"Stored Hash: {student.password_hash}")
            print(f"Entered Password: {password}")

        if student and check_password_hash(student.password_hash,password):
            # Store student ID in the session for tracking logged-in student
            session["user_id"] = student.id
            flash("Login successful!", "success")
            return redirect(url_for("profile"))  # Redirect to profile page
        else:
            flash("Invalid credentials. Please try again.", "error")
            return redirect(url_for("login"))

    return render_template("login.html")

# Student Profile Route (View and Update Personal Info)
@app.route("/profile", methods=["GET", "POST"])
def profile():
    if "user_id" not in session:
        flash("Please log in to access your profile.", "error")
        return redirect(url_for("login"))

    # Fetch student data from the database
    student = Student.query.get(session["user_id"])

    if request.method == "POST":
        # Update student details based on form input
        student.name = request.form.get("name")
        student.email = request.form.get("email")
        student.phone = request.form.get("phone")
        student.age = request.form.get("age")
        student.branch = request.form.get("branch")
        student.highest_qualification = request.form.get("highest_qualification")
        student.grad_year = request.form.get("grad_year")
        student.program = request.form.get("training_program")

        try:
            db.session.commit()  # Save updates to the database
            flash("Profile updated successfully!", "success")
        except Exception as e:
            db.session.rollback()
            flash("Error updating profile. Please try again.", "error")

        return redirect(url_for("profile"))  # Reload updated profile

    return render_template("profile.html", student=student)

# Student Logout Route
@app.route("/logout")
def logout():
    session.pop("user_id", None)  # Remove student from session
    flash("Logged out successfully.", "success")
    return redirect(url_for("login"))


@app.route("/")
def home():
    return redirect(url_for("signup"))
SECRET_PASSWORD = "listofstudents"  # Admin password

# Admin Login Route
@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        password = request.form.get("password")

        # Validate admin password
        if password == SECRET_PASSWORD:
            session["admin_logged_in"] = True
            flash("Admin login successful!", "success")
            return redirect(url_for("admin_dashboard"))

        flash("Invalid password. Try again.", "error")
        return redirect(url_for("admin_login"))

    return render_template("admin_login.html")

# Admin Dashboard Route (View Registered Students)
@app.route("/admin")
def admin_dashboard():
    # Restrict access to logged-in admins
    if not session.get("admin_logged_in"):
        flash("Unauthorized access. Please log in as admin.", "error")
        return redirect(url_for("admin_login"))

    # Fetch all registered students
    students = Student.query.all()
    return render_template("students.html", students=students)

# Admin Logout Route
@app.route("/admin_logout")
def admin_logout():
    session.pop("admin_logged_in", None)  # Clear admin session
    flash("Admin logged out successfully.", "success")
    return redirect(url_for("admin_login"))





if __name__ == "__main__":
    app.run(debug=True)
