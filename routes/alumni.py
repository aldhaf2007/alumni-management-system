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
        import os
        from werkzeug.utils import secure_filename
        from flask import current_app
        
        # Handle profile picture upload
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and file.filename != '':
                filename = secure_filename(f"user_{current_user.id}_{file.filename}")
                upload_path = os.path.join('static', 'uploads', 'profile_pics')
                os.makedirs(upload_path, exist_ok=True)
                file.save(os.path.join(upload_path, filename))
                current_user.profile.profile_picture = filename

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

@alumni_bp.route('/feedback', methods=['GET', 'POST'])
def feedback():
    from models import Feedback
    if request.method == 'POST':
        subject = request.form.get('subject')
        message = request.form.get('message')
        if subject and message:
            new_feedback = Feedback(user_id=current_user.id, subject=subject, message=message)
            db.session.add(new_feedback)
            db.session.commit()
            flash('Your feedback has been submitted successfully.', 'success')
            return redirect(url_for('alumni.feedback'))
        else:
            flash('Please fill out all fields.', 'danger')
            
    return render_template('alumni/feedback.html')

@alumni_bp.route('/report', methods=['POST'])
def report_item():
    from models import Report
    reported_type = request.form.get('reported_type')
    reported_id = request.form.get('reported_id')
    reason = request.form.get('reason')
    
    if reported_type and reported_id and reason:
        new_report = Report(
            reporter_id=current_user.id,
            reported_type=reported_type,
            reported_id=int(reported_id),
            reason=reason
        )
        db.session.add(new_report)
        db.session.commit()
        flash('Report submitted successfully. An admin will review it.', 'success')
    else:
        flash('Failed to submit report. Missing information.', 'danger')
        
    # Redirect back to where they came from
    return redirect(request.referrer or url_for('public.index'))
