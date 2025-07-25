# auth.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db
import sqlite3
import re
from functools import wraps

auth = Blueprint('auth', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in first.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def validate_password(password):
    """Check if password meets minimum requirements"""
    if len(password) < 8:
        return False
    if not re.search("[a-z]", password):
        return False
    if not re.search("[A-Z]", password):
        return False
    if not re.search("[0-9]", password):
        return False
    return True

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Validation
        if not all([name, email, phone, password, confirm_password]):
            flash('All fields are required.', 'error')
            return render_template('register.html')

        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('register.html')

        if not validate_password(password):
            flash('Password must be at least 8 characters long and contain uppercase, lowercase, and numbers.', 'error')
            return render_template('register.html')

        try:
            db = get_db()
            cursor = db.cursor()
            
            # Check if email already exists
            cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
            if cursor.fetchone() is not None:
                flash('Email already registered.', 'error')
                return render_template('register.html')

            # Insert new user
            hashed_password = generate_password_hash(password)
            cursor.execute(
                "INSERT INTO users (name, email, phone, password) VALUES (?, ?, ?, ?)",
                (name, email, phone, hashed_password)
            )
            db.commit()
            
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth.login'))

        except sqlite3.Error as e:
            flash('An error occurred during registration.', 'error')
            print(f"Database error: {e}")  # Log the error
            return render_template('register.html')

    return render_template('register.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        if not email or not password:
            flash('Both email and password are required.', 'error')
            return render_template('login.html')

        try:
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            user = cursor.fetchone()

            if user and check_password_hash(user['password'], password):
                session.clear()
                session['user_id'] = user['id']
                session['user_name'] = user['name']
                flash(f'Welcome back, {user["name"]}!', 'success')
                return redirect(url_for('dashboard.user_dashboard'))
            else:
                flash('Invalid email or password.', 'error')

        except sqlite3.Error as e:
            flash('An error occurred during login.', 'error')
            print(f"Database error: {e}")  # Log the error

    return render_template('login.html')

@auth.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('home'))

@auth.route('/profile')
@login_required
def profile():
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],))
        user = cursor.fetchone()
        
        if user:
            return render_template('profile.html', user=user)
        else:
            flash('User not found.', 'error')
            return redirect(url_for('home'))

    except sqlite3.Error as e:
        flash('An error occurred while loading your profile.', 'error')
        print(f"Database error: {e}")  # Log the error
        return redirect(url_for('home'))

@auth.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')

        try:
            db = get_db()
            cursor = db.cursor()
            
            # Get current user data
            cursor.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],))
            user = cursor.fetchone()

            if not user:
                flash('User not found.', 'error')
                return redirect(url_for('auth.profile'))

            # Update name and phone
            if name and phone:
                cursor.execute(
                    "UPDATE users SET name = ?, phone = ? WHERE id = ?",
                    (name, phone, session['user_id'])
                )

            # Update password if provided
            if current_password and new_password:
                if not check_password_hash(user['password'], current_password):
                    flash('Current password is incorrect.', 'error')
                    return redirect(url_for('auth.profile'))

                if not validate_password(new_password):
                    flash('New password does not meet requirements.', 'error')
                    return redirect(url_for('auth.profile'))

                hashed_password = generate_password_hash(new_password)
                cursor.execute(
                    "UPDATE users SET password = ? WHERE id = ?",
                    (hashed_password, session['user_id'])
                )

            db.commit()
            flash('Profile updated successfully.', 'success')
            return redirect(url_for('auth.profile'))

        except sqlite3.Error as e:
            flash('An error occurred while updating your profile.', 'error')
            print(f"Database error: {e}")  # Log the error
            return redirect(url_for('auth.profile'))

    return redirect(url_for('auth.profile'))