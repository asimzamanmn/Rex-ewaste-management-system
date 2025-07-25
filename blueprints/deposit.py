# blueprints/deposit.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database import get_db
from blueprints.auth import login_required
import os
from werkzeug.utils import secure_filename

deposit = Blueprint('deposit', __name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@deposit.route('/create', methods=['GET', 'POST'])
@login_required
def create_deposit():
    if request.method == 'POST':
        location = request.form.get('location')
        collection_point = request.form.get('collection_point')
        component = request.form.get('component')
        build_no = request.form.get('build_no')
        model_id = request.form.get('model_id')
        
        # File handling
        photo = request.files.get('photo')
        photo_path = None
        
        if photo and allowed_file(photo.filename):
            filename = secure_filename(photo.filename)
            photo_path = os.path.join(UPLOAD_FOLDER, filename)
            photo.save(photo_path)

        try:
            db = get_db()
            cursor = db.cursor()
            cursor.execute("""
                INSERT INTO deposits (user_id, location, collection_point, component, 
                                    build_no, model_id, photos, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (session['user_id'], location, collection_point, component, 
                 build_no, model_id, photo_path, 'pending'))
            db.commit()
            flash('Deposit registered successfully!', 'success')
            return redirect(url_for('dashboard.user_dashboard'))
            
        except Exception as e:
            flash('Error creating deposit. Please try again.', 'error')
            print(f"Deposit error: {e}")
            
    return render_template('deposit.html')

@deposit.route('/history')
@login_required
def deposit_history():
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            SELECT * FROM deposits 
            WHERE user_id = ? 
            ORDER BY created_at DESC
        """, (session['user_id'],))
        deposits = cursor.fetchall()
        return render_template('deposit_history.html', deposits=deposits)
    except Exception as e:
        flash('Error retrieving deposit history.', 'error')
        print(f"Deposit history error: {e}")
        return render_template('deposit_history.html', deposits=[])