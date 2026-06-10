from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from modules.database import get_db
from werkzeug.security import generate_password_hash, check_password_hash
import random, time, smtplib, ssl, os
from email.message import EmailMessage

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
        
        if user and check_password_hash(user['password'], password):
            session['user'] = {'id': user['id'], 'username': user['username'],
                               'role': user['role'], 'name': user['name']}
            return redirect(url_for('dashboard'))
        flash('Invalid username or password. Please try again.', 'error')
    return render_template('login.html')

@auth_bp.route('/register', methods=['POST'])
def register():
    name     = request.form.get('reg_name', '').strip()
    username = request.form.get('reg_username', '').strip()
    password = request.form.get('reg_password', '').strip()
    confirm  = request.form.get('reg_confirm', '').strip()
    role     = request.form.get('reg_role', 'employee')

    if not name or not username or not password:
        flash('All fields are required.', 'reg_error')
        return redirect(url_for('auth.login') + '#register')

    if password != confirm:
        flash('Passwords do not match.', 'reg_error')
        return redirect(url_for('auth.login') + '#register')

    if len(password) < 6:
        flash('Password must be at least 6 characters.', 'reg_error')
        return redirect(url_for('auth.login') + '#register')

    db = get_db()
    existing = db.execute("SELECT id FROM users WHERE username=?", (username,)).fetchone()
    if existing:
        flash('Username already taken. Please choose another.', 'reg_error')
        return redirect(url_for('auth.login') + '#register')

    email = request.form.get('reg_email', '').strip()
    hashed_pw = generate_password_hash(password)
    db.execute("INSERT INTO users (username, password, role, name, email) VALUES (?,?,?,?,?)",
               (username, hashed_pw, role, name, email))
    db.commit()
    flash(f'Account created! Welcome, {name}. Please sign in.', 'reg_success')
    return redirect(url_for('auth.login'))

# In-memory OTP store: {email: {'otp': '123456', 'expires': timestamp}}
_otp_store = {}

def send_email_otp(receiver_email, otp):
    from dotenv import dotenv_values
    config = dotenv_values('.env')
    sender_email = config.get('GMAIL_USER')
    sender_password = config.get('GMAIL_APP_PASSWORD')
    
    if not sender_email or not sender_password:
        print("Warning: GMAIL_USER or GMAIL_APP_PASSWORD not set in .env.")
        return False

    msg = EmailMessage()
    msg.set_content(f"Your OTP is {otp}.\nThis OTP is valid for 5 minutes.\nDo not share this OTP with anyone.")
    msg['Subject'] = 'Restaurant App Password Reset OTP'
    msg['From'] = sender_email
    msg['To'] = receiver_email

    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"SMTP Error: {e}")
        return False

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        if not email:
            flash('Please enter your email.', 'error')
            return redirect(url_for('auth.forgot_password'))
            
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        if not user:
            flash('No account found with that email address.', 'error')
            return redirect(url_for('auth.forgot_password'))
            
        otp = str(random.randint(100000, 999999))
        _otp_store[email] = {'otp': otp, 'expires': time.time() + 300}
        
        session['reset_email'] = email
        
        if send_email_otp(email, otp):
            flash('OTP has been sent to your email.', 'success')
        else:
            flash(f'Failed to send email. Demo OTP is {otp}', 'error')
            
        return redirect(url_for('auth.verify_otp'))
        
    return render_template('forgot_password.html')

@auth_bp.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    email = session.get('reset_email')
    if not email:
        return redirect(url_for('auth.forgot_password'))
        
    if request.method == 'POST':
        otp_entered = request.form.get('otp', '').strip()
        record = _otp_store.get(email)
        
        if not record:
            flash('No OTP requested or session expired. Please try again.', 'error')
            return redirect(url_for('auth.forgot_password'))
            
        if time.time() > record['expires']:
            del _otp_store[email]
            flash('OTP expired. Please request a new one.', 'error')
            return redirect(url_for('auth.forgot_password'))
            
        if otp_entered != record['otp']:
            flash('Invalid OTP. Please try again.', 'error')
            return redirect(url_for('auth.verify_otp'))
            
        session['otp_verified'] = True
        return redirect(url_for('auth.reset_password'))
        
    return render_template('verify_otp.html')

@auth_bp.route('/resend-otp', methods=['POST'])
def resend_otp():
    email = session.get('reset_email')
    if not email:
        return redirect(url_for('auth.forgot_password'))
        
    otp = str(random.randint(100000, 999999))
    _otp_store[email] = {'otp': otp, 'expires': time.time() + 300}
    
    if send_email_otp(email, otp):
        flash('A new OTP has been sent to your email.', 'success')
    else:
        flash(f'Failed to send email. Demo OTP is {otp}', 'error')
        
    return redirect(url_for('auth.verify_otp'))

@auth_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    email = session.get('reset_email')
    if not email or not session.get('otp_verified'):
        flash('Unauthorized access.', 'error')
        return redirect(url_for('auth.login'))
        
    if request.method == 'POST':
        new_password = request.form.get('password', '').strip()
        confirm = request.form.get('confirm', '').strip()
        
        if len(new_password) < 6:
            flash('Password must be at least 6 characters.', 'error')
            return redirect(url_for('auth.reset_password'))
            
        if new_password != confirm:
            flash('Passwords do not match.', 'error')
            return redirect(url_for('auth.reset_password'))
            
        hashed_pw = generate_password_hash(new_password)
        db = get_db()
        db.execute("UPDATE users SET password=? WHERE email=?", (hashed_pw, email))
        db.commit()
        
        # Cleanup
        if email in _otp_store:
            del _otp_store[email]
        session.pop('reset_email', None)
        session.pop('otp_verified', None)
        
        flash('Password reset successfully! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('reset_password.html')

@auth_bp.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('auth.login'))

@auth_bp.route('/users')
def users():
    if 'user' not in session or session['user']['role'] != 'admin':
        return redirect(url_for('dashboard'))
    db = get_db()
    users = db.execute("SELECT * FROM users ORDER BY created_at DESC").fetchall()
    return render_template('users.html', users=users, user=session['user'])

@auth_bp.route('/users/add', methods=['POST'])
def add_user():
    if 'user' not in session or session['user']['role'] != 'admin':
        return redirect(url_for('dashboard'))
    db = get_db()
    existing = db.execute("SELECT id FROM users WHERE username=?", (request.form['username'],)).fetchone()
    if existing:
        flash('Username already exists!', 'error')
        return redirect(url_for('auth.users'))
        
    hashed_pw = generate_password_hash(request.form['password'])
    db.execute("INSERT INTO users (username, password, role, name, email) VALUES (?,?,?,?,?)",
               (request.form['username'], hashed_pw,
                request.form['role'], request.form['name'], request.form.get('email','')))
    db.commit()
    flash('User added successfully', 'success')
    return redirect(url_for('auth.users'))

@auth_bp.route('/users/delete/<int:uid>')
def delete_user(uid):
    if 'user' not in session or session['user']['role'] != 'admin':
        return redirect(url_for('dashboard'))
    db = get_db()
    db.execute("DELETE FROM users WHERE id=? AND id!=1", (uid,))
    db.commit()
    flash('User removed', 'success')
    return redirect(url_for('auth.users'))
