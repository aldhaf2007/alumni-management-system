from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import Profile, User
from extensions import db

alumni_bp = Blueprint('alumni', __name__)

@alumni_bp.before_request
@login_required
def require_alumni():
    if current_user.role != 'alumni' and current_user.role != 'admin':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('public.index'))

@alumni_bp.route('/dashboard')
def dashboard():
    return render_template('alumni/dashboard.html')

@alumni_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    # If the user doesn't have a profile yet, create an empty one
    if not current_user.profile:
        new_profile = Profile(user_id=current_user.id)
        db.session.add(new_profile)
        db.session.commit()
    
    if request.method == 'POST':
        current_user.profile.batch = request.form.get('batch')
        current_user.profile.department = request.form.get('department')
        current_user.profile.company = request.form.get('company')
        current_user.profile.designation = request.form.get('designation')
        current_user.profile.location = request.form.get('location')
        current_user.profile.skills = request.form.get('skills')
        current_user.profile.bio = request.form.get('bio')
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('alumni.profile'))

    return render_template('alumni/profile.html', profile=current_user.profile)

@alumni_bp.route('/directory')
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
    
    return render_template('alumni/directory.html', profiles=alumni_profiles, search=search,
                           selected_batch=batch, selected_department=department,
                           batches=sorted(batches), departments=sorted(departments))
