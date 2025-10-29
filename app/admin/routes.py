from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps
from app import db
from app.admin import admin_bp
from app.admin.forms import ZendeskSettingsForm, UserManagementForm
from app.models import User, ZendeskSettings
from app.tools.registry import ToolRegistry
from app.zendesk.client import ZendeskClientManager


def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('You need administrator privileges to access this page.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/')
@login_required
@admin_required
def index():
    """Admin dashboard"""
    # Get statistics
    user_count = User.query.count()
    admin_count = User.query.filter_by(role='admin').count()
    tool_count = len(ToolRegistry.get_all_tools())

    # Get Zendesk settings status
    zendesk_settings = ZendeskSettings.get_active_settings()
    zendesk_configured = zendesk_settings is not None

    return render_template('admin/index.html',
                         title='Admin Panel',
                         user_count=user_count,
                         admin_count=admin_count,
                         tool_count=tool_count,
                         zendesk_configured=zendesk_configured)


@admin_bp.route('/zendesk', methods=['GET', 'POST'])
@login_required
@admin_required
def zendesk_settings():
    """Manage Zendesk API settings"""
    form = ZendeskSettingsForm()

    # Get existing settings
    settings = ZendeskSettings.get_active_settings()

    if form.validate_on_submit():
        if settings:
            # Update existing settings
            settings.subdomain = form.subdomain.data
            settings.email = form.email.data
            settings.api_token = form.api_token.data
        else:
            # Create new settings
            settings = ZendeskSettings(
                subdomain=form.subdomain.data,
                email=form.email.data,
                api_token=form.api_token.data,
                is_active=True
            )
            db.session.add(settings)

        db.session.commit()

        # Clear the client cache to use new credentials
        ZendeskClientManager.clear_client()

        flash('Zendesk settings saved successfully!', 'success')
        return redirect(url_for('admin.zendesk_settings'))

    # Pre-populate form with existing settings
    if settings and request.method == 'GET':
        form.subdomain.data = settings.subdomain
        form.email.data = settings.email
        # Don't pre-populate API token for security

    return render_template('admin/zendesk_settings.html',
                         title='Zendesk Settings',
                         form=form,
                         has_settings=settings is not None)


@admin_bp.route('/zendesk/test')
@login_required
@admin_required
def test_zendesk():
    """Test Zendesk connection"""
    try:
        client = ZendeskClientManager.get_client()
        if client:
            # Try to fetch current user to test connection
            current_user_info = client.users.me()
            flash(f'Connection successful! Connected as: {current_user_info.email}', 'success')
        else:
            flash('Zendesk credentials not configured. Please configure them first.', 'warning')
    except Exception as e:
        flash(f'Connection failed: {str(e)}', 'danger')

    return redirect(url_for('admin.zendesk_settings'))


@admin_bp.route('/users')
@login_required
@admin_required
def users():
    """List all users"""
    all_users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', title='User Management', users=all_users)


@admin_bp.route('/users/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_user():
    """Create a new user"""
    form = UserManagementForm()

    if form.validate_on_submit():
        # Check if username or email already exists
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already exists.', 'danger')
            return render_template('admin/user_form.html', title='Create User', form=form, is_edit=False)

        if User.query.filter_by(email=form.email.data).first():
            flash('Email already exists.', 'danger')
            return render_template('admin/user_form.html', title='Create User', form=form, is_edit=False)

        user = User(
            username=form.username.data,
            email=form.email.data,
            role=form.role.data,
            active=form.active.data
        )
        user.set_password(form.password.data)

        db.session.add(user)
        db.session.commit()

        flash(f'User {user.username} created successfully!', 'success')
        return redirect(url_for('admin.users'))

    # Set default values for new user
    form.active.data = True
    form.role.data = 'user'

    return render_template('admin/user_form.html', title='Create User', form=form, is_edit=False)


@admin_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    """Edit an existing user"""
    user = User.query.get_or_404(user_id)
    form = UserManagementForm()

    if form.validate_on_submit():
        # Check if username changed and if new username exists
        if user.username != form.username.data:
            if User.query.filter_by(username=form.username.data).first():
                flash('Username already exists.', 'danger')
                return render_template('admin/user_form.html', title='Edit User', form=form, is_edit=True, user=user)

        # Check if email changed and if new email exists
        if user.email != form.email.data:
            if User.query.filter_by(email=form.email.data).first():
                flash('Email already exists.', 'danger')
                return render_template('admin/user_form.html', title='Edit User', form=form, is_edit=True, user=user)

        user.username = form.username.data
        user.email = form.email.data
        user.role = form.role.data
        user.active = form.active.data

        # Only update password if provided
        if form.password.data:
            user.set_password(form.password.data)

        db.session.commit()
        flash(f'User {user.username} updated successfully!', 'success')
        return redirect(url_for('admin.users'))

    # Pre-populate form
    if request.method == 'GET':
        form.username.data = user.username
        form.email.data = user.email
        form.role.data = user.role
        form.active.data = user.active

    return render_template('admin/user_form.html', title='Edit User', form=form, is_edit=True, user=user)


@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """Delete a user"""
    user = User.query.get_or_404(user_id)

    # Prevent deleting yourself
    if user.id == current_user.id:
        flash('You cannot delete your own account!', 'danger')
        return redirect(url_for('admin.users'))

    username = user.username
    db.session.delete(user)
    db.session.commit()

    flash(f'User {username} deleted successfully!', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/tools')
@login_required
@admin_required
def tools():
    """View all registered tools"""
    all_tools = ToolRegistry.get_all_tools()
    tools_by_category = {}

    for slug, tool_class in all_tools.items():
        category = tool_class.category
        if category not in tools_by_category:
            tools_by_category[category] = []
        tools_by_category[category].append({
            'name': tool_class.name,
            'slug': tool_class.slug,
            'description': tool_class.description,
            'requires_admin': tool_class.requires_admin
        })

    return render_template('admin/tools.html',
                         title='Registered Tools',
                         tools_by_category=tools_by_category)
