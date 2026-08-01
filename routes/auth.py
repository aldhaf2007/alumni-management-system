from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models import User
from extensions import db, bcrypt

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('public.index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password_hash, password):
            if user.status != 'Approved':
                flash('Your account is pending admin approval.', 'warning')
                return redirect(url_for('auth.login'))
            
            login_user(user)
            flash('Login successful.', 'success')
            
            # Smart Redirection
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            
            # Redirect based on role if no specific page was requested
            if user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            elif user.role == 'alumni':
                return redirect(url_for('alumni.dashboard'))
            else:
                return redirect(url_for('student.dashboard'))
        else:
            flash('Login unsuccessful. Please check email and password.', 'danger')
            
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('public.index'))
        
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role') # 'alumni' or 'student'
        
        # In MVP we only allow alumni and students to register. Admins are created manually.
        if role not in ['alumni', 'student']:
            flash('Invalid role selected.', 'danger')
            return redirect(url_for('auth.register'))
            
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already exists.', 'danger')
            return redirect(url_for('auth.register'))
            
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(name=name, email=email, password_hash=hashed_password, role=role, status='Pending')
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please wait for admin approval before logging in.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('public.index'))
