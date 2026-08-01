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
            
        event = Event(title=title, description=description, date=date_obj, time=time_obj, location=location, created_by=current_user.id)
        db.session.add(event)
        db.session.commit()
        flash('Event created successfully.', 'success')
        return redirect(url_for('events.list_events'))
        
    return render_template('events/create.html')

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
