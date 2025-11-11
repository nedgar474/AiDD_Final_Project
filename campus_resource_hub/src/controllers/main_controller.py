# AI Contribution: Generated initial scaffold, verified by team.
from flask import Blueprint, render_template, current_app, redirect, url_for
from flask_login import current_user, login_required
from datetime import datetime
from ..models.resource import Resource
from ..models.booking import Booking

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    # Get featured resources for the homepage (only published)
    featured_resources = Resource.query.filter_by(is_featured=True, status='published').limit(6).all()
    categories = Resource.query.filter_by(status='published').with_entities(Resource.category).distinct().all()
    return render_template('index.html', featured_resources=featured_resources, categories=categories)

@main_bp.route('/dashboard')
@login_required
def dashboard():
    # Get user's active bookings
    active_bookings = Booking.query.filter_by(
        user_id=current_user.id,
        status='active'
    ).count()
    
    # Get user's pending bookings
    pending_bookings = Booking.query.filter_by(
        user_id=current_user.id,
        status='pending'
    ).count()
    
    # Get recent activities (bookings)
    recent_activities = Booking.query.filter_by(
        user_id=current_user.id
    ).order_by(Booking.created_at.desc()).limit(5).all()
    
    # Get upcoming bookings
    upcoming_bookings = Booking.query.filter(
        Booking.user_id == current_user.id,
        Booking.status == 'active',
        Booking.end_date >= datetime.utcnow()
    ).order_by(Booking.start_date.asc()).limit(5).all()
    
    context = {
        'active_bookings': active_bookings,
        'pending_bookings': pending_bookings,
        'recent_activities': recent_activities,
        'upcoming_bookings': upcoming_bookings
    }
    
    return render_template('dashboard.html', **context)