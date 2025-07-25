# blueprints/pickup.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database import get_db
from blueprints.auth import login_required
from datetime import datetime, timedelta

pickup = Blueprint('pickup', __name__)

@pickup.route('/request', methods=['GET', 'POST'])
@login_required
def request_pickup():
    if request.method == 'POST':
        pickup_date = request.form.get('pickup_date')
        address = request.form.get('address')
        notes = request.form.get('notes')
        
        try:
            db = get_db()
            cursor = db.cursor()
            
            # Create pickup request
            cursor.execute("""
                INSERT INTO pickups (user_id, pickup_date, address, notes, status)
                VALUES (?, ?, ?, ?, ?)
            """, (session['user_id'], pickup_date, address, notes, 'pending'))
            
            db.commit()
            flash('Pickup request submitted successfully!', 'success')
            return redirect(url_for('dashboard.user_dashboard'))
            
        except Exception as e:
            flash('Error submitting pickup request.', 'error')
            print(f"Pickup request error: {e}")
    
    # Get available dates (next 7 days, excluding weekends)
    available_dates = []
    current_date = datetime.now()
    for i in range(7):
        date = current_date + timedelta(days=i)
        if date.weekday() < 5:  # Monday = 0, Friday = 4
            available_dates.append(date.strftime('%Y-%m-%d'))
    
    return render_template('pickup.html', available_dates=available_dates)

@pickup.route('/history')
@login_required
def pickup_history():
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            SELECT * FROM pickups 
            WHERE user_id = ? 
            ORDER BY created_at DESC
        """, (session['user_id'],))
        pickups = cursor.fetchall()
        return render_template('pickup_history.html', pickups=pickups)
    except Exception as e:
        flash('Error retrieving pickup history.', 'error')
        print(f"Pickup history error: {e}")
        return render_template('pickup_history.html', pickups=[])

@pickup.route('/cancel/<int:pickup_id>', methods=['POST'])
@login_required
def cancel_pickup(pickup_id):
    try:
        db = get_db()
        cursor = db.cursor()
        
        # Verify ownership and status
        cursor.execute("""
            SELECT * FROM pickups 
            WHERE id = ? AND user_id = ? AND status = 'pending'
        """, (pickup_id, session['user_id']))
        pickup = cursor.fetchone()
        
        if pickup:
            cursor.execute("""
                UPDATE pickups 
                SET status = 'cancelled' 
                WHERE id = ?
            """, (pickup_id,))
            db.commit()
            flash('Pickup request cancelled successfully.', 'success')
        else:
            flash('Invalid pickup request or already processed.', 'error')
            
    except Exception as e:
        flash('Error cancelling pickup request.', 'error')
        print(f"Pickup cancellation error: {e}")
        
    return redirect(url_for('pickup.pickup_history'))