from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, send_from_directory
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
import uuid
from models import Job, JobApplication
from extensions import db

jobs_bp = Blueprint('jobs', __name__)

@jobs_bp.route('/jobs')
@login_required
def list_jobs():
    jobs = Job.query.order_by(Job.created_at.desc()).all()
    return render_template('jobs/list.html', jobs=jobs)

@jobs_bp.route('/jobs/post', methods=['GET', 'POST'])
@login_required
def post_job():
    if current_user.role == 'student':
        flash('Students cannot post jobs.', 'danger')
        return redirect(url_for('jobs.list_jobs'))
        
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        company = request.form.get('company')
        location = request.form.get('location')
        
        job = Job(title=title, description=description, company=company, location=location, posted_by=current_user.id)
        db.session.add(job)
        db.session.commit()
        flash('Job posted successfully.', 'success')
        return redirect(url_for('jobs.list_jobs'))
        
    return render_template('jobs/post.html')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'pdf'

@jobs_bp.route('/jobs/<int:job_id>/apply', methods=['GET', 'POST'])
@login_required
def apply_job(job_id):
    job = Job.query.get_or_404(job_id)
    if current_user.id == job.posted_by:
        flash("You cannot apply to your own job post.", "danger")
        return redirect(url_for('jobs.list_jobs'))

    if request.method == 'POST':
        cover_letter = request.form.get('cover_letter')
        resume = request.files.get('resume')
        
        if not resume or resume.filename == '':
            flash('No resume selected.', 'danger')
            return redirect(request.url)
            
        if resume and allowed_file(resume.filename):
            filename = secure_filename(resume.filename)
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            resume.save(os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename))
            
            application = JobApplication(job_id=job.id, user_id=current_user.id, cover_letter=cover_letter, resume_link=unique_filename)
            db.session.add(application)
            db.session.commit()
            
            flash('Your application has been submitted successfully.', 'success')
            return redirect(url_for('jobs.list_jobs'))
        else:
            flash('Only PDF files are allowed.', 'danger')
            
    return render_template('jobs/apply.html', job=job)

@jobs_bp.route('/jobs/<int:job_id>/applications')
@login_required
def view_applications(job_id):
    job = Job.query.get_or_404(job_id)
    if current_user.id != job.posted_by and current_user.role != 'admin':
        flash("Unauthorized.", "danger")
        return redirect(url_for('jobs.list_jobs'))
        
    applications = JobApplication.query.filter_by(job_id=job.id).all()
    return render_template('jobs/applications.html', job=job, applications=applications)

@jobs_bp.route('/download_resume/<filename>')
@login_required
def download_resume(filename):
    # Only simple access control for MVP (should be stricter in prod)
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
