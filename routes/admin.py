from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import User, Profile, Job, Event, JobApplication, event_registrations
from extensions import db, bcrypt
import csv
from io import StringIO
from flask import Response

admin_bp = Blueprint('admin', __name__)

@admin_bp.before_request
@login_required
def require_admin():
    if current_user.role != 'admin':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('public.index'))

@admin_bp.route('/dashboard')
def dashboard():
    pending_users = User.query.filter_by(status='Pending').all()
    approved_users = User.query.filter(User.status == 'Approved', User.role != 'admin').all()
    return render_template('admin/dashboard.html', pending_users=pending_users, approved_users=approved_users)

@admin_bp.route('/approve_user/<int:user_id>', methods=['POST'])
def approve_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.status == 'Pending':
        user.status = 'Approved'
        # Create an empty profile for the approved user
        if not user.profile:
            profile = Profile(user_id=user.id)
            db.session.add(profile)
        db.session.commit()
        flash(f'User {user.name} approved successfully.', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/reject_user/<int:user_id>', methods=['POST'])
def reject_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.status == 'Pending':
        user.status = 'Rejected'
        db.session.commit()
        flash(f'User {user.name} rejected.', 'info')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/export/users')
def export_users():
    users = User.query.all()
    
    def generate():
        data = StringIO()
        writer = csv.writer(data)
        
        # Write header
        writer.writerow(['ID', 'Name', 'Email', 'Role', 'Status'])
        yield data.getvalue()
        data.seek(0)
        data.truncate(0)
        
        # Write rows
        for user in users:
            writer.writerow([user.id, user.name, user.email, user.role, user.status])
            yield data.getvalue()
            data.seek(0)
            data.truncate(0)
            
    return Response(generate(), mimetype='text/csv', headers={"Content-Disposition": "attachment; filename=users.csv"})

@admin_bp.route('/users')
def manage_users():
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/users/add', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')
        status = request.form.get('status')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return redirect(url_for('admin.add_user'))
            
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(name=name, email=email, password_hash=hashed_password, role=role, status=status)
        db.session.add(user)
        db.session.commit()
        
        if status == 'Approved' and role != 'admin':
            profile = Profile(user_id=user.id)
            db.session.add(profile)
            db.session.commit()
            
        flash('User added successfully.', 'success')
        return redirect(url_for('admin.manage_users'))
        
    return render_template('admin/user_add.html')

@admin_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        user.name = request.form.get('name')
        user.email = request.form.get('email')
        user.role = request.form.get('role')
        new_status = request.form.get('status')
        
        if new_status == 'Approved' and user.status != 'Approved' and user.role != 'admin':
            if not user.profile:
                profile = Profile(user_id=user.id)
                db.session.add(profile)
                
        user.status = new_status
        db.session.commit()
        flash('User updated successfully.', 'success')
        return redirect(url_for('admin.manage_users'))
        
    return render_template('admin/user_edit.html', user=user)

@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('You cannot delete your own account.', 'danger')
        return redirect(url_for('admin.manage_users'))
        
    db.session.delete(user)
    db.session.commit()
    flash(f'User {user.name} was successfully deleted.', 'success')
    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/reports')
def reports():
    # User Demographics
    total_alumni = User.query.filter_by(role='alumni').count()
    total_students = User.query.filter_by(role='student').count()
    total_admins = User.query.filter_by(role='admin').count()
    
    # Account Status
    approved_users = User.query.filter_by(status='Approved').count()
    pending_users = User.query.filter_by(status='Pending').count()
    rejected_users = User.query.filter_by(status='Rejected').count()
    
    # Engagement and Participation
    total_jobs = Job.query.count()
    total_events = Event.query.count()
    total_job_applications = JobApplication.query.count()
    total_event_registrations = db.session.query(event_registrations).count()
    
    # Department Distribution
    from sqlalchemy import func
    dept_distribution = db.session.query(Profile.department, func.count(Profile.id))\
        .join(User)\
        .filter(User.role == 'alumni', Profile.department != None, Profile.department != '')\
        .group_by(Profile.department).all()
        
    dept_labels = [d[0] for d in dept_distribution]
    dept_data = [d[1] for d in dept_distribution]
    
    return render_template('admin/reports.html',
                           demographics=[total_alumni, total_students, total_admins],
                           statuses=[approved_users, pending_users, rejected_users],
                           engagement=[total_events, total_event_registrations, total_jobs, total_job_applications],
                           dept_labels=dept_labels,
                           dept_data=dept_data)
