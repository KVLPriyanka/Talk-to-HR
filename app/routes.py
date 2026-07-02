"""
Flask routes and API endpoints for HR Portal
"""
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime
from app.models import db, User, Ticket

# Create blueprints: one for data endpoints, one for web pages
api = Blueprint('api', __name__, url_prefix='/api')
pages = Blueprint('pages', __name__)

# ============================================================================
# Authentication Helpers
# ============================================================================
def login_required(f):
    """Decorator for routes that require login."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function

def hr_required(f):
    """Decorator for routes that require HR role."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        
        user = User.query.get(session['username'])
        if not user or user.role != 'HR':
            return jsonify({'error': 'Forbidden'}), 403
        return f(*args, **kwargs)
    return decorated_function

# ============================================================================
# Authentication Routes
# ============================================================================
@api.route('/auth/login', methods=['POST'])
def login():
    """Login endpoint."""
    data = request.get_json()
    username = data.get('username', '').lower()
    password = data.get('password', '')
    
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400
    
    user = User.query.get(username)
    if not user or not user.verify_password(password):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    if not user.is_active:
        return jsonify({'error': 'Account inactive'}), 403
    
    session['username'] = user.username
    session['role'] = user.role
    session['full_name'] = user.full_name
    session.permanent = True
    
    return jsonify({
        'success': True,
        'user': user.to_dict()
    })

@api.route('/auth/logout', methods=['POST'])
def logout():
    """Logout endpoint."""
    session.clear()
    return jsonify({'success': True})

@api.route('/auth/register', methods=['POST'])
def register():
    """Register new user endpoint."""
    data = request.get_json()
    username = data.get('username', '').lower()
    password = data.get('password', '')
    full_name = data.get('full_name', '')
    mobile_number = data.get('mobile_number', '')
    employee_id = data.get('employee_id', '')
    
    # Validation
    if not all([username, password, full_name, mobile_number, employee_id]):
        return jsonify({'error': 'All fields required'}), 400
    
    if not mobile_number.isdigit() or len(mobile_number) != 10:
        return jsonify({'error': 'Mobile number must be 10 digits'}), 400
    
    if User.query.get(username):
        return jsonify({'error': 'User already exists'}), 409
    
    # Create user
    user = User(
        username=username,
        full_name=full_name,
        mobile_number=mobile_number,
        employee_id=employee_id,
        role='Applicant'
    )
    user.set_password(password)
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'User created successfully'}), 201

@api.route('/auth/reset-password', methods=['POST'])
def reset_password():
    """Reset password endpoint."""
    data = request.get_json()
    username = data.get('username', '').lower()
    employee_id = data.get('employee_id', '')
    mobile_number = data.get('mobile_number', '')
    new_password = data.get('new_password', '')
    
    if not all([username, employee_id, mobile_number, new_password]):
        return jsonify({'error': 'All fields required'}), 400
    
    user = User.query.get(username)
    if not user or user.employee_id != employee_id or user.mobile_number != mobile_number or not user.is_active:
        return jsonify({'error': 'Invalid credentials'}), 401
    
    user.set_password(new_password)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Password reset successfully'})

@api.route('/auth/current', methods=['GET'])
def get_current_user():
    """Get current logged-in user."""
    if 'username' not in session:
        return jsonify({'user': None})
    
    user = User.query.get(session['username'])
    if user:
        return jsonify({'user': user.to_dict()})
    
    session.clear()
    return jsonify({'user': None})

# ============================================================================
# Ticket Routes (Applicant)
# ============================================================================
@api.route('/tickets', methods=['GET'])
@login_required
def get_user_tickets():
    """Get tickets for current user."""
    username = session['username']
    tickets = Ticket.query.filter_by(username=username).order_by(Ticket.id.desc()).all()
    
    return jsonify({
        'tickets': [ticket.to_dict() for ticket in tickets]
    })

@api.route('/tickets', methods=['POST'])
@login_required
def create_ticket():
    """Create new ticket."""
    data = request.get_json()
    username = session['username']
    
    ticket_type = data.get('type', '')
    subject = data.get('subject', '')
    description = data.get('description', '')
    
    if not all([ticket_type, subject, description]):
        return jsonify({'error': 'All fields required'}), 400
    
    ticket = Ticket(
        username=username,
        type=ticket_type,
        subject=subject,
        description=description
    )
    
    db.session.add(ticket)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Ticket created successfully',
        'ticket': ticket.to_dict()
    }), 201

@api.route('/tickets/<int:ticket_id>', methods=['GET'])
@login_required
def get_ticket(ticket_id):
    """Get specific ticket."""
    ticket = Ticket.query.get(ticket_id)
    
    if not ticket:
        return jsonify({'error': 'Ticket not found'}), 404
    
    # Check if user has access
    if ticket.username != session['username']:
        user = User.query.get(session['username'])
        if user.role != 'HR':
            return jsonify({'error': 'Forbidden'}), 403
    
    return jsonify({'ticket': ticket.to_dict()})

# ============================================================================
# HR Management Routes
# ============================================================================
@api.route('/tickets/all', methods=['GET'])
@hr_required
def get_all_tickets():
    """Get all tickets (HR only)."""
    tickets = Ticket.query.order_by(Ticket.id.desc()).all()
    return jsonify({
        'tickets': [ticket.to_dict() for ticket in tickets]
    })

@api.route('/tickets/<int:ticket_id>', methods=['PUT'])
@hr_required
def update_ticket(ticket_id):
    """Update ticket status and notes (HR only)."""
    data = request.get_json()
    ticket = Ticket.query.get(ticket_id)
    
    if not ticket:
        return jsonify({'error': 'Ticket not found'}), 404
    
    status = data.get('status')
    hr_notes = data.get('hr_notes')
    
    if status:
        ticket.status = status
    if hr_notes:
        ticket.hr_notes = hr_notes
    
    ticket.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Ticket updated',
        'ticket': ticket.to_dict()
    })

@api.route('/users', methods=['GET'])
@hr_required
def get_all_users():
    """Get all users (HR only)."""
    users = User.query.order_by(User.username).all()
    return jsonify({
        'users': [user.to_dict() for user in users]
    })

@api.route('/users/<username>/toggle', methods=['POST'])
@hr_required
def toggle_user_status(username):
    """Toggle user active/inactive status (HR only)."""
    user = User.query.get(username)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    user.is_active = not user.is_active
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'User {username} is now {"active" if user.is_active else "inactive"}',
        'user': user.to_dict()
    })

# ============================================================================
# Page Routes (Registered directly to Root "/" to prevent JS Redirect Loops)
# ============================================================================
@pages.route('/', methods=['GET'])
def index():
    """Serve main login page."""
    return render_template('index.html')

@pages.route('/dashboard', methods=['GET'])
def dashboard():
    """Serve applicant dashboard."""
    if 'username' not in session:
        return redirect(url_for('pages.index'))
    
    user = User.query.get(session['username'])
    if not user:
        session.clear()
        return redirect(url_for('pages.index'))
    
    return render_template('dashboard.html', user=user)

@pages.route('/hr-dashboard', methods=['GET'])
def hr_dashboard():
    """Serve HR dashboard."""
    if 'username' not in session:
        return redirect(url_for('pages.index'))
    
    user = User.query.get(session['username'])
    if not user or user.role != 'HR':
        return redirect(url_for('pages.index'))
    
    return render_template('hr-dashboard.html', user=user)