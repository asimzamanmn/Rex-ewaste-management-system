# blueprints/dashboard.py
from flask import Blueprint, render_template, session
from database import get_db
from blueprints.auth import login_required

dashboard = Blueprint('dashboard', __name__)

@dashboard.route('/dashboard')
@login_required
def user_dashboard():
    try:
        db = get_db()
        cursor = db.cursor()
        
        # Get user's deposits
        cursor.execute("""
            SELECT * FROM deposits 
            WHERE user_id = ? 
            ORDER BY created_at DESC
        """, (session['user_id'],))
        deposits = cursor.fetchall()
        
        # Get user's points
        cursor.execute("""
            SELECT points FROM users 
            WHERE id = ?
        """, (session['user_id'],))
        user = cursor.fetchone()
        points = user['points'] if user else 0
        
        return render_template('dashboard.html', 
                             deposits=deposits, 
                             points=points,
                             user_name=session.get('user_name'))
                             
    except Exception as e:
        print(f"Dashboard error: {e}")  # Log the error
        return render_template('dashboard.html', 
                             deposits=[], 
                             points=0,
                             user_name=session.get('user_name'))