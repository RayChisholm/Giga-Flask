# Claude Code Context - Zendesk Bulk Operations Tool

**Last Updated**: 2025-10-27
**Status**: Phase 1 Complete with Enhanced UI/UX - MVP Running

This document contains technical context, implementation details, and common patterns for Claude Code to reference when working on this project.

---

## Project Overview

Flask web application for performing bulk operations on Zendesk data with a plugin-based tool system for easy extensibility.

**Core Technology Stack**:
- Flask 3.0.0 (web framework)
- Flask-SQLAlchemy 3.1.1 (ORM)
- Flask-Login 0.6.3 (authentication)
- Flask-WTF 1.2.1 (forms)
- zenpy 2.0.50 (Zendesk API client)
- Bootstrap 5.3.2 (UI framework, via CDN)
- Custom CSS & JavaScript for enhanced UX

**Database**: SQLite (development) at `/instance/app.db`

---

## Frontend Assets & UI/UX Features

### Custom Stylesheets
**Location**: `app/static/css/custom.css`

**Key Features**:
- Modern gradient designs for buttons and welcome sections
- Smooth transitions and hover effects
- Loading spinner overlay for async operations
- Enhanced form controls with better focus states
- Responsive design optimizations
- Print-friendly styles
- Accessibility improvements (focus outlines, skip links)

**CSS Variables** (for consistency):
```css
--primary-color: #0d6efd
--success-color: #198754
--danger-color: #dc3545
--border-radius: 8px
--box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1)
--transition: all 0.3s ease
```

### Custom JavaScript
**Location**: `app/static/js/app.js`

**Key Features**:
- **Loading States**: Automatic spinner overlay for form submissions
- **Tooltips**: Bootstrap tooltip initialization
- **Form Enhancements**:
  - Real-time validation feedback
  - Character counters for textareas
  - Floating label effects
- **Table Enhancements**:
  - Auto-generated search boxes for large tables
  - Clickable rows
- **Keyboard Shortcuts** (macOS-optimized):
  - `Cmd + K` (⌘K): Go to Dashboard
  - `Cmd + Shift + A` (⌘⇧A): Go to Admin Panel (if admin)
  - `Cmd + Shift + D` (⌘⇧D): Toggle dark mode
  - `Cmd + /` (⌘/): Focus search input
  - `Cmd + Enter` (⌘↵): Submit active form
  - `ESC`: Cancel/Go back
- **Dark Mode**:
  - Toggle button in navbar with moon/sun icon
  - Uses `data-theme` attribute on `<html>` element
  - Preference saved in localStorage
  - System preference detection on first visit
  - Comprehensive CSS variables for theming
- **Utility Functions**:
  - `showLoadingSpinner()` / `hideLoadingSpinner()`
  - `showSuccessMessage(message)`
  - `confirmAction(message)`
  - `copyToClipboard(text)`
  - `debounce(func, wait)`

**Global Object**: `window.GigaFlask` - Contains all exported functions

### UI Improvements

**Landing Page Enhancements**:
- Gradient welcome banner with personalized greeting
- Quick stats cards (Available Tools, Categories, Quick & Easy)
- Improved tool cards with consistent heights
- Feature showcase cards (Getting Started, Safe & Reliable, Export Results)
- Keyboard shortcuts reference card

**Form Improvements**:
- Better validation feedback with visual indicators
- Loading states on submit buttons
- Character counters for long text fields
- Enhanced focus states

**Table Improvements**:
- Auto-search for tables with 10+ rows
- Clickable rows (if they contain links)
- Better hover states
- Sortable columns (future enhancement)

**General UX**:
- Auto-dismissing alerts (5 seconds)
- Smooth scroll behavior
- Favicon (wrench emoji)
- Better mobile responsiveness
- Tooltips for additional context

---

## Key Architecture Decisions

### 1. Tool System (Plugin Architecture)

**The most important scalability feature**. All tools inherit from `BaseTool` and use a decorator-based registry system.

**Base Tool Location**: `app/tools/base_tool.py`

**Key Methods**:
- `get_form_fields()`: Returns list of form field definitions
- `validate_input(form_data)`: Returns (bool, error_message)
- `execute(form_data)`: Returns dict with `success`, `message`, `data`
- `get_template()`: Override for custom templates (default: `tools/tool_base.html`)
- `get_export_formats()`: Returns list of supported export formats (['csv', 'json'])
- `export_results(results, format)`: Export results in specified format. Returns (bytes, mimetype, filename)

**Tool Registration Pattern**:
```python
from app.tools.base_tool import BaseTool
from app.tools.registry import ToolRegistry

@ToolRegistry.register
class NewTool(BaseTool):
    name = "Tool Display Name"
    slug = "url-slug"
    description = "What the tool does"
    category = "Category Name"
    requires_admin = False

    def get_form_fields(self):
        return [
            {
                'name': 'field_name',
                'label': 'Field Label',
                'type': 'text',  # text, textarea, number, select, checkbox
                'required': True,
                'placeholder': 'Placeholder text',
                'help_text': 'Help text shown below field',
                'options': [...]  # For select fields: [{'value': 'x', 'label': 'X'}]
            }
        ]

    def validate_input(self, form_data):
        if not form_data.get('field_name'):
            return False, "Error message"
        return True, None

    def execute(self, form_data):
        try:
            # Implementation here
            return {
                'success': True,
                'message': 'Success message',
                'data': {'key': 'value'}
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error: {str(e)}',
                'data': None
            }
```

**Important**: After creating a tool, import it in `app/tools/implementations/__init__.py`:
```python
from app.tools.implementations.my_tool import MyTool
```

### 2. Zendesk Client Management

**Location**: `app/zendesk/client.py`

**Singleton Pattern**: `ZendeskClientManager` maintains a single client instance.

**Usage in Tools**:
```python
from app.zendesk.client import ZendeskClientManager

client = ZendeskClientManager.get_client()
if not client:
    raise Exception("Zendesk not configured")
```

**Common Operations** (`app/zendesk/helpers.py`):
- `get_all_views()`: Fetch all views
- `get_all_macros()`: Fetch all macros
- `get_view_tickets(view_id, limit)`: Fetch tickets from view
- `search_macros_by_text(search_term)`: Search macros by content
- `apply_macro_to_ticket(ticket_id, macro_id)`: Apply macro to single ticket
- `apply_macro_to_tickets(ticket_ids, macro_id, delay)`: Apply macro to multiple tickets with rate limiting

**Credentials**: Stored in `ZendeskSettings` model or environment variables as fallback.

### 3. Authentication & Authorization

**Login Required**: Use `@login_required` decorator from `flask_login`

**Admin Required**: Use custom `@admin_required` decorator:
```python
from app.admin.routes import admin_required

@admin_bp.route('/admin-only')
@login_required
@admin_required
def admin_function():
    pass
```

**Check in Tool**: Set `requires_admin = True` in tool class.

**Current User**: Access via `current_user` (Flask-Login):
```python
from flask_login import current_user

if current_user.is_admin():
    # Admin logic
```

### 4. Database Models

**Location**: `app/models.py`

**User Model**:
- Fields: `id`, `username`, `email`, `password_hash`, `role`, `active`, `created_at`
- Methods: `set_password()`, `check_password()`, `is_admin()`

**ZendeskSettings Model**:
- Fields: `id`, `subdomain`, `email`, `api_token`, `last_updated`, `is_active`
- Static method: `get_active_settings()`

**Creating Migrations** (if you add new models/fields):
```bash
flask db migrate -m "Description"
flask db upgrade
```

---

## File Structure Reference

```
app/
├── __init__.py                 # App factory, extension initialization
├── config.py                   # Config classes (Development, Production, Testing)
├── models.py                   # Database models
│
├── auth/                       # Authentication blueprint
│   ├── __init__.py
│   ├── routes.py              # Login, logout, register routes
│   └── forms.py               # LoginForm, RegistrationForm
│
├── admin/                      # Admin panel blueprint
│   ├── __init__.py
│   ├── routes.py              # Admin dashboard, user mgmt, settings
│   └── forms.py               # ZendeskSettingsForm, UserManagementForm
│
├── main/                       # Main pages blueprint
│   ├── __init__.py
│   └── routes.py              # Landing page (tool grid)
│
├── tools/                      # Tool system (THE CORE)
│   ├── __init__.py
│   ├── base_tool.py           # Abstract base class
│   ├── registry.py            # Tool auto-discovery and registration
│   ├── routes.py              # Generic tool execution routes
│   └── implementations/       # Individual tool files
│       ├── __init__.py        # Import all tools here
│       ├── macro_search.py    # Macro search tool
│       └── apply_macro_to_view.py  # Apply macro to view tool
│
├── zendesk/                    # Zendesk integration
│   ├── __init__.py
│   ├── client.py              # ZendeskClientManager (singleton)
│   └── helpers.py             # Common Zendesk operations
│
├── templates/                  # Jinja2 templates
│   ├── base.html              # Base layout with Bootstrap
│   ├── auth/
│   │   ├── login.html
│   │   └── register.html
│   ├── admin/
│   │   ├── index.html         # Admin dashboard
│   │   ├── zendesk_settings.html
│   │   ├── users.html
│   │   ├── user_form.html
│   │   └── tools.html
│   ├── main/
│   │   └── index.html         # Tool grid dashboard
│   └── tools/
│       └── tool_base.html     # Generic tool template
│
└── static/                     # CSS, JS, images
    ├── css/
    ├── js/
    └── img/
```

---

## Common Development Tasks

### Adding a New Tool

1. **Create tool file**: `app/tools/implementations/my_new_tool.py`
2. **Implement BaseTool**: Follow pattern above
3. **Import in**: `app/tools/implementations/__init__.py`
4. **Restart server**: Tool auto-registers on import

### Adding a New Form Field Type

Edit `app/templates/tools/tool_base.html` and add new field type handling:
```html
{% elif field.type == 'new_type' %}
    <!-- New field type HTML here -->
{% endif %}
```

### Custom Tool Template

1. Create template: `app/templates/tools/my_tool.html`
2. Extend base: `{% extends "tools/tool_base.html" %}`
3. Override in tool:
```python
def get_template(self):
    return 'tools/my_tool.html'
```

### Accessing Zendesk API

Always use the client manager:
```python
from app.zendesk.client import ZendeskClientManager

client = ZendeskClientManager.get_client()
if not client:
    # Handle not configured

# Use zenpy API
tickets = client.tickets()
macros = client.macros()
views = client.views()
```

### Database Operations

```python
from app import db
from app.models import User

# Query
user = User.query.filter_by(username='admin').first()
all_users = User.query.all()

# Create
new_user = User(username='test', email='test@example.com')
new_user.set_password('password')
db.session.add(new_user)
db.session.commit()

# Update
user.email = 'newemail@example.com'
db.session.commit()

# Delete
db.session.delete(user)
db.session.commit()
```

---

## Known Issues & Solutions

### Issue: Werkzeug Import Error

**Problem**: `ImportError: cannot import name 'url_parse' from 'werkzeug.urls'`

**Solution**: Use `from urllib.parse import urlparse` instead of `from werkzeug.urls import url_parse`

**Location**: `app/auth/routes.py:3`

### Issue: Database Not Found

**Problem**: `sqlite3.OperationalError: unable to open database file`

**Solution**: Use absolute path in `.env`:
```
DATABASE_URL=sqlite:////Users/justin/Desktop/Claude/Giga Flask/instance/app.db
```

### Issue: Tool Not Showing Up

**Problem**: Created tool but it doesn't appear in dashboard

**Solution**:
1. Check tool is imported in `app/tools/implementations/__init__.py`
2. Restart Flask server
3. Check console for "Registered tool: ..." message

---

## Environment Variables

**Location**: `.env` file (root directory)

**Required Variables**:
```
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=<change-in-production>
DATABASE_URL=sqlite:////absolute/path/to/instance/app.db
```

**Optional Zendesk Variables** (can also configure in admin panel):
```
ZENDESK_SUBDOMAIN=your-subdomain
ZENDESK_EMAIL=email@example.com
ZENDESK_TOKEN=your-api-token
```

---

## Flask CLI Commands

**Custom Commands** (defined in `run.py`):
```bash
flask init-db          # Initialize database tables
flask create-admin     # Interactive admin user creation
```

**Standard Flask Commands**:
```bash
flask run              # Start dev server
flask shell            # Open Python shell with app context
```

**Database Migrations**:
```bash
flask db init          # Initialize migrations (already done)
flask db migrate -m "message"  # Create migration
flask db upgrade       # Apply migrations
flask db downgrade     # Rollback migration
```

---

## Bootstrap 5 Components Used

**Grid System**: 12-column responsive grid
**Cards**: `.card`, `.card-body`, `.card-header`
**Buttons**: `.btn`, `.btn-primary`, `.btn-outline-*`
**Forms**: `.form-control`, `.form-select`, `.form-check`
**Alerts**: `.alert`, `.alert-success`, `.alert-danger`
**Badges**: `.badge`, `.bg-success`, `.bg-danger`
**Navigation**: `.navbar`, `.breadcrumb`

**Icons**: Bootstrap Icons via CDN
- Usage: `<i class="bi bi-house-door"></i>`
- Browse: https://icons.getbootstrap.com/

---

## Jinja2 Template Patterns

**Extending Base**:
```html
{% extends "base.html" %}

{% block title %}Page Title{% endblock %}

{% block content %}
<!-- Your content here -->
{% endblock %}
```

**URL Generation**:
```html
<a href="{{ url_for('main.index') }}">Home</a>
<a href="{{ url_for('tools.execute_tool', slug='macro-search') }}">Tool</a>
```

**Flash Messages** (already handled in base.html):
```python
flash('Message text', 'success')  # success, danger, warning, info
```

**Current User**:
```html
{% if current_user.is_authenticated %}
    Welcome, {{ current_user.username }}!
{% endif %}
```

---

## API Rate Limiting Considerations

Zendesk has rate limits. For bulk operations:

1. **Track request count** in tool
2. **Add delays** between requests:
```python
import time
for item in items:
    # Do operation
    time.sleep(1)  # 1 second delay
```
3. **Handle 429 responses**:
```python
from zenpy.lib.exception import RateLimitException
try:
    # API call
except RateLimitException:
    # Wait and retry
```

---

## Testing Approach

**Manual Testing Checklist**:
- [ ] User can log in/out
- [ ] Admin can access admin panel
- [ ] Standard user cannot access admin panel
- [ ] Zendesk credentials can be configured
- [ ] Connection test works
- [ ] Tools appear in dashboard
- [ ] Tool execution works
- [ ] Form validation works
- [ ] Results display correctly
- [ ] Error messages are helpful

**Future**: Add unit tests in `tests/` directory

---

## Security Notes

**IMPORTANT FOR PRODUCTION**:
1. Change `SECRET_KEY` in `.env`
2. Use strong passwords
3. Consider encrypting `api_token` in database
4. Use HTTPS
5. Set `FLASK_ENV=production`
6. Use production WSGI server (gunicorn, uWSGI)
7. Set up proper user permissions
8. Regular backups of database

**Never Commit**:
- `.env` file
- `instance/` directory
- Any files with credentials

---

## Future Enhancements (Roadmap)

### Phase 2: Additional Tools
- Apply macro to all tickets in view
- Bulk tag add/remove
- Bulk ticket deletion (with safety checks)
- String search within tickets
- Bulk field updates

### Phase 3: Advanced Features
- Async task processing (Celery)
- Progress indicators for long operations
- Export to CSV/JSON
- Scheduled operations
- Operation history/audit log
- Rollback capabilities

### Phase 4: Production Ready
- PostgreSQL migration
- Docker containerization
- CI/CD pipeline
- Comprehensive testing
- API for programmatic access
- Multi-tenant support

---

## Debugging Tips

**Enable SQL Echo**:
In `app/config.py`, set `SQLALCHEMY_ECHO = True` in `DevelopmentConfig`

**Flask Debug Mode**:
Already enabled in development. Shows detailed error pages and auto-reloads.

**Check Tool Registration**:
Look for console output: `Registered tool: [Name] ([slug])`

**Database Inspection**:
```bash
sqlite3 instance/app.db
.tables
.schema users
SELECT * FROM users;
.quit
```

**Access Flask Shell**:
```bash
flask shell
>>> from app.models import User
>>> User.query.all()
>>> exit()
```

---

## Quick Reference: Running the App

```bash
# Activate virtual environment
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# Run development server
python run.py
# OR
flask run

# Access at: http://127.0.0.1:5000
# Default admin: admin / admin123
```

---

## Contact & Resources

**Documentation**:
- Flask: https://flask.palletsprojects.com/
- zenpy: https://github.com/facetoe/zenpy
- Zendesk API: https://developer.zendesk.com/api-reference/
- Bootstrap 5: https://getbootstrap.com/docs/5.3/

**Project Files**:
- `PROJECT_PLAN.md`: Detailed architectural plan
- `USER_GUIDE.md`: End-user documentation
- `CLAUDE_CONTEXT.md`: This file (technical reference)

---

**End of Context Document**
