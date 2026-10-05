from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import Event, Announcement, User
from extensions import db

events_bp = Blueprint('events', __name__)

@events_bp.route('/events')
@login_required
def list_events():
    events = Event.query.order_by(Event.date.desc()).all()
    return render_template('events/list.html', events=events)

@events_bp.route('/events/create', methods=['GET', 'POST'])
@login_required
def create_event():
    if current_user.role != 'admin':
        flash('Only admins can create events.', 'danger')
        return redirect(url_for('events.list_events'))
        
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        date_str = request.form.get('date')
        time_str = request.form.get('time')
        location = request.form.get('location')
        
        from datetime import datetime
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            date_obj = None
            
        try:
            time_obj = datetime.strptime(time_str, '%H:%M').time()
        except (ValueError, TypeError):
            time_obj = None
            
        import os
        from werkzeug.utils import secure_filename
        
        image_filename = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '':
                # Generate unique filename to avoid overwrites
                image_filename = secure_filename(f"event_{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}")
                upload_path = os.path.join('static', 'uploads', 'event_pics')
                os.makedirs(upload_path, exist_ok=True)
                file.save(os.path.join(upload_path, image_filename))
        
        event = Event(title=title, description=description, date=date_obj, time=time_obj, location=location, image=image_filename, created_by=current_user.id)
        db.session.add(event)
        db.session.commit()
        flash('Event created successfully.', 'success')
        return redirect(url_for('events.list_events'))
        
    return render_template('events/create.html')

@events_bp.route('/events/<int:event_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    if current_user.role != 'admin':
        flash('Only admins can edit events.', 'danger')
        return redirect(url_for('events.list_events'))
        
    event = Event.query.get_or_404(event_id)
    if request.method == 'POST':
        event.title = request.form.get('title')
        event.description = request.form.get('description')
        event.location = request.form.get('location')
        
        from datetime import datetime
        try:
            event.date = datetime.strptime(request.form.get('date'), '%Y-%m-%d').date()
        except (ValueError, TypeError):
            pass
            
        try:
            event.time = datetime.strptime(request.form.get('time'), '%H:%M').time()
        except (ValueError, TypeError):
            pass

        import os
        from werkzeug.utils import secure_filename
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '':
                image_filename = secure_filename(f"event_{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}")
                upload_path = os.path.join('static', 'uploads', 'event_pics')
                os.makedirs(upload_path, exist_ok=True)
                file.save(os.path.join(upload_path, image_filename))
                event.image = image_filename
                
        db.session.commit()
        flash('Event updated successfully.', 'success')
        return redirect(url_for('events.list_events'))

    return render_template('events/edit.html', event=event)

@events_bp.route('/events/<int:event_id>/delete', methods=['POST'])
@login_required
def delete_event(event_id):
    if current_user.role != 'admin':
        flash('Only admins can delete events.', 'danger')
        return redirect(url_for('events.list_events'))
        
    event = Event.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    flash('Event deleted successfully.', 'success')
    return redirect(url_for('events.list_events'))

@events_bp.route('/announcements')
@login_required
def list_announcements():
    announcements = Announcement.query.order_by(Announcement.created_at.desc()).all()
    return render_template('events/announcements.html', announcements=announcements)

@events_bp.route('/announcements/create', methods=['GET', 'POST'])
@login_required
def create_announcement():
    if current_user.role != 'admin':
        flash('Only admins can create announcements.', 'danger')
        return redirect(url_for('events.list_announcements'))
        
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        type = request.form.get('type')
        
        ann = Announcement(title=title, content=content, type=type, posted_by=current_user.id)
        db.session.add(ann)
        db.session.commit()
        flash('Announcement posted.', 'success')
        return redirect(url_for('events.list_announcements'))
        
    return render_template('events/create_announcement.html')

@events_bp.route('/announcements/<int:ann_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_announcement(ann_id):
    if current_user.role != 'admin':
        flash('Only admins can edit announcements.', 'danger')
        return redirect(url_for('events.list_announcements'))
        
    ann = Announcement.query.get_or_404(ann_id)
    if request.method == 'POST':
        ann.title = request.form.get('title')
        ann.content = request.form.get('content')
        ann.type = request.form.get('type')
        db.session.commit()
        flash('Announcement updated.', 'success')
        return redirect(url_for('events.list_announcements'))

    return render_template('events/edit_announcement.html', announcement=ann)

@events_bp.route('/announcements/<int:ann_id>/delete', methods=['POST'])
@login_required
def delete_announcement(ann_id):
    if current_user.role != 'admin':
        flash('Only admins can delete announcements.', 'danger')
        return redirect(url_for('events.list_announcements'))
        
    ann = Announcement.query.get_or_404(ann_id)
    db.session.delete(ann)
    db.session.commit()
    flash('Announcement deleted.', 'success')
    return redirect(url_for('events.list_announcements'))

@events_bp.route('/events/<int:event_id>/rsvp', methods=['POST'])
@login_required
def rsvp(event_id):
    event = Event.query.get_or_404(event_id)
    if current_user not in event.attendees:
        event.attendees.append(current_user)
        db.session.commit()
        flash('Successfully registered for the event!', 'success')
    else:
        flash('You are already registered.', 'info')
    return redirect(url_for('events.list_events'))
