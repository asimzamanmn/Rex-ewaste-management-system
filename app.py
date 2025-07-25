# app.py
from flask import Flask, render_template, flash
from blueprints.auth import auth
from blueprints.dashboard import dashboard
from blueprints.deposit import deposit
from blueprints.rewards import rewards
from blueprints.pickup import pickup
from database import init_app, init_db
import os
from blueprints.chatbot_ewaste import chatbot_ewaste_bp

# Create Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)  # More secure secret key

# Register blueprints
app.register_blueprint(auth, url_prefix='/auth')
app.register_blueprint(dashboard, url_prefix='/dashboard')
app.register_blueprint(deposit, url_prefix='/deposit')
app.register_blueprint(rewards, url_prefix='/rewards')
app.register_blueprint(pickup, url_prefix='/pickup')
app.register_blueprint(chatbot_ewaste_bp, url_prefix='/ewaste_chat')

# Initialize database
init_app(app)

@app.route('/')
def home():
    return render_template('home.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    with app.app_context():
        init_db()  # Initialize database tables
    app.run(debug=True)