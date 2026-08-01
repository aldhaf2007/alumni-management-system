from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import Profile, User
from extensions import db

student_bp = Blueprint('student', __name__)

@student_bp.before_request
@login_required
def require_student():
    if current_user.role != 'student' and current_user.role != 'admin':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('public.index'))

@student_bp.route('/dashboard')
def dashboard():
    return render_template('student/dashboard.html')

@student_bp.route('/directory')
def directory():
    search = request.args.get('q', '')
    batch = request.args.get('batch', '')
    department = request.args.get('department', '')
    
    query = Profile.query.join(User).filter(User.role == 'alumni', User.status == 'Approved')
    
    if search:
        search_fmt = f"%{search}%"
        query = query.filter(
            (User.name.ilike(search_fmt)) |
            (Profile.company.ilike(search_fmt)) |
            (Profile.skills.ilike(search_fmt)) |
            (Profile.location.ilike(search_fmt))
        )
        
    if batch:
        query = query.filter(Profile.batch == batch)
        
    if department:
        query = query.filter(Profile.department == department)
        
    alumni_profiles = query.all()
    
    batches = [b[0] for b in db.session.query(Profile.batch).filter(Profile.batch != None, Profile.batch != '').distinct().all()]
    departments = [d[0] for d in db.session.query(Profile.department).filter(Profile.department != None, Profile.department != '').distinct().all()]
    
    return render_template('student/directory.html', profiles=alumni_profiles, search=search,
                           selected_batch=batch, selected_department=department,
                           batches=sorted(batches), departments=sorted(departments))
