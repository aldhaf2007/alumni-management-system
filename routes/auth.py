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
            else:
                return redirect(url_for('alumni.dashboard'))
        else:
            flash('Login unsuccessful. Please check email and password.', 'danger')
            
    return render_template('auth/login.html')

import re

def is_strong_password(password):
    if not password or len(password) < 8: return False
    if not re.search(r'[A-Z]', password): return False
    if not re.search(r'[a-z]', password): return False
    if not re.search(r'\d', password): return False
    return True

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('public.index'))
        
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        role = 'alumni'
            
        if not is_strong_password(password):
            flash('Password must be at least 8 characters and contain an uppercase letter, lowercase letter, and a number.', 'danger')
            return redirect(url_for('auth.register'))
            
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already exists.', 'danger')
            return redirect(url_for('auth.register'))
            
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(name=name, email=email, password_hash=hashed_password, role=role, status='Pending')
        
        db.session.add(user)
        db.session.flush() # To get the user ID
        
        # Now create Profile with extra details
        from models import Profile
        profile = Profile(
            user_id=user.id,
            batch=request.form.get('batch'),
            department=request.form.get('department'),
            company=request.form.get('company'),
            designation=request.form.get('designation'),
            location=request.form.get('location'),
            skills=request.form.get('skills'),
            bio=request.form.get('bio')
        )
        db.session.add(profile)
        
        db.session.commit()
        
        flash('Registration successful! Please wait for admin approval before logging in.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('public.index'))
