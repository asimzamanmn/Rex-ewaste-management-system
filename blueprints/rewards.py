# blueprints/rewards.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database import get_db
from blueprints.auth import login_required

rewards = Blueprint('rewards', __name__)

@rewards.route('/view')
@login_required
def view_rewards():
    try:
        db = get_db()
        cursor = db.cursor()
        
        # Get user's total points
        cursor.execute("SELECT points FROM users WHERE id = ?", (session['user_id'],))
        user = cursor.fetchone()
        points = user['points'] if user else 0
        
        # Get available rewards (you'll need to create this table)
        cursor.execute("SELECT * FROM rewards ORDER BY points_required")
        available_rewards = cursor.fetchall()
        
        return render_template('rewards.html', 
                             points=points, 
                             rewards=available_rewards)
    except Exception as e:
        flash('Error loading rewards.', 'error')
        print(f"Rewards error: {e}")
        return render_template('rewards.html', points=0, rewards=[])

@rewards.route('/redeem/<int:reward_id>', methods=['POST'])
@login_required
def redeem_reward(reward_id):
    try:
        db = get_db()
        cursor = db.cursor()
        
        # Get reward details
        cursor.execute("SELECT * FROM rewards WHERE id = ?", (reward_id,))
        reward = cursor.fetchone()
        
        # Get user's points
        cursor.execute("SELECT points FROM users WHERE id = ?", (session['user_id'],))
        user = cursor.fetchone()
        
        if not reward or not user:
            flash('Invalid reward selection.', 'error')
            return redirect(url_for('rewards.view_rewards'))
            
        if user['points'] < reward['points_required']:
            flash('Insufficient points.', 'error')
            return redirect(url_for('rewards.view_rewards'))
            
        # Deduct points and record redemption
        cursor.execute("""
            UPDATE users 
            SET points = points - ? 
            WHERE id = ?
        """, (reward['points_required'], session['user_id']))
        
        cursor.execute("""
            INSERT INTO redemptions (user_id, reward_id, points_used)
            VALUES (?, ?, ?)
        """, (session['user_id'], reward_id, reward['points_required']))
        
        db.commit()
        flash('Reward redeemed successfully!', 'success')
        
    except Exception as e:
        flash('Error redeeming reward.', 'error')
        print(f"Reward redemption error: {e}")
        
    return redirect(url_for('rewards.view_rewards'))