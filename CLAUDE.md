# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Flask web application for performing bulk operations on Zendesk data with a plugin-based tool architecture. The core design allows easy addition of new tools by inheriting from `BaseTool` and using the `@ToolRegistry.register` decorator.

## Development Commands

```bash
# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database (first time setup)
flask init-db

# Create admin user (interactive)
flask create-admin

# Run development server
flask run
# Or: python run.py

# Access Flask shell with database context
flask shell

# Database migrations (after model changes)
flask db migrate -m "Description of changes"
flask db upgrade
```

## Application Architecture

### Application Factory Pattern

The app uses Flask's application factory pattern in `app/__init__.py`:
- `create_app(config_name)` initializes extensions (SQLAlchemy, Flask-Migrate, Flask-Login)
- Blueprints are registered for different modules: auth, admin, main, tools
- Configuration loaded from `app/config.py` with environment-specific classes

### Blueprint Structure

```
app/
├── auth/           # Authentication (login/logout)
├── admin/          # Admin panel (user management, Zendesk config)
├── main/           # Dashboard and landing pages
├── tools/          # Tool system (CORE ARCHITECTURE)
└── zendesk/        # Zendesk API integration
```

### Tool System Architecture (Plugin Pattern)

The tool system is the central scalability feature. All tools follow this pattern:

**1. Base Tool Interface** (`app/tools/base_tool.py`):
- Abstract base class that all tools inherit from
- Defines required metadata: `name`, `slug`, `description`, `category`, `requires_admin`
- Abstract methods: `get_form_fields()`, `validate_input()`, `execute()`
- Optional methods: `get_template()`, `get_export_formats()`, `export_results()`

**2. Tool Registry** (`app/tools/registry.py`):
- Singleton registry for auto-discovering tools
- Tools self-register using `@ToolRegistry.register` decorator
- Provides lookup by slug, category filtering, and tool enumeration
- No manual route registration needed

**3. Generic Tool Routes** (`app/tools/routes.py`):
- Single route `/tools/<slug>` handles ALL tools dynamically
- Fetches tool from registry, validates input, executes, displays results
- Export route `/tools/<slug>/export/<format>` handles result exports
- Results stored in session for export functionality

**4. Tool Implementations** (`app/tools/implementations/`):
- Each tool is a separate file that inherits from `BaseTool`
- Must be imported in `app/tools/implementations/__init__.py` to trigger registration
- Tool instances are created on-demand by the registry

### Zendesk Integration

**Client Manager** (`app/zendesk/client.py`):
- `ZendeskClientManager` is a singleton that manages Zenpy client instances
- Credentials sourced from database (via `ZendeskSettings` model) or environment variables
- Client is cached and reused; automatically refreshed if credentials change
- Methods: `get_client()`, `test_connection()`, `clear_client()`, `is_configured()`

**Helper Functions** (`app/zendesk/helpers.py`):
- Common Zendesk operations used by multiple tools
- Example: `search_macros_by_text()` fetches all macros and searches within actions

### Database Models

**User** (`app/models.py`):
- Flask-Login integration with `UserMixin`
- Fields: username, email, password_hash, role (admin/user), active, created_at
- Password hashing via werkzeug.security
- Role-based access: `is_admin()` method

**ZendeskSettings** (`app/models.py`):
- Stores Zendesk API credentials (subdomain, email, api_token)
- `get_active_settings()` retrieves current active configuration
- Credentials can be set via admin panel or environment variables

## Adding a New Tool

To add a new tool, create a file in `app/tools/implementations/`:

```python
from app.tools.base_tool import BaseTool
from app.tools.registry import ToolRegistry

@ToolRegistry.register
class MyNewTool(BaseTool):
    name = "My Tool Name"
    slug = "my-tool-slug"
    description = "What this tool does"
    category = "Category Name"
    requires_admin = False  # Set True for admin-only

    def get_form_fields(self):
        return [
            {
                'name': 'field_name',
                'label': 'Field Label',
                'type': 'text',  # text, textarea, select, checkbox, number
                'required': True,
                'placeholder': 'Enter value...',
                'help_text': 'Help text for user'
            }
        ]

    def validate_input(self, form_data):
        # Return (is_valid, error_message)
        if not form_data.get('field_name'):
            return False, "Field is required"
        return True, None

    def execute(self, form_data):
        # Implement tool logic here
        # Use ZendeskClientManager.get_client() for API access
        try:
            # Your implementation
            return {
                'success': True,
                'message': 'Success message',
                'data': {'results': []}
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error: {str(e)}',
                'data': None
            }
```

Then import it in `app/tools/implementations/__init__.py`:

```python
from app.tools.implementations.my_new_tool import MyNewTool
```

The tool will automatically appear in the dashboard. No route changes needed.

## Configuration

Configuration is environment-based (`app/config.py`):
- `DevelopmentConfig`: DEBUG=True, SQLite database, SQL echo off by default
- `ProductionConfig`: DEBUG=False, should use PostgreSQL
- `TestingConfig`: In-memory SQLite, CSRF disabled

Environment variables (`.env`):
- `FLASK_ENV`: development/production
- `SECRET_KEY`: Session encryption key (MUST change for production)
- `DATABASE_URL`: Database connection string
- `ZENDESK_SUBDOMAIN`, `ZENDESK_EMAIL`, `ZENDESK_TOKEN`: Optional, can be set via admin panel

## Key Design Patterns

1. **Tool Plugin System**: Abstract base class + decorator-based registration enables adding tools without modifying core routes
2. **Singleton Client Manager**: Single Zenpy client instance reused across requests, automatically refreshed on credential changes
3. **Generic Tool Routes**: One route handles all tools dynamically via registry lookup
4. **Blueprint Modularity**: Each feature area (auth, admin, tools) is a separate blueprint with isolated routes and templates

## Async Job System (Celery + Redis)

For large-scale operations (>500 tickets), the application uses Celery with Redis for background job processing:

### Architecture

**Job Flow**:
1. Tool checks if `ticket_limit > 500` and `supports_async() == True`
2. If async: create Job record, generate UUID, dispatch Celery task, redirect to job status page
3. Celery task updates Job model progress every batch of tickets
4. UI polls `/jobs/<id>/status` API endpoint every 2 seconds for updates
5. On completion: results stored in Job.result_data as JSON

**Key Components**:
- `celery_app.py`: Celery application with Flask context integration
- `app/celery_config.py`: Celery configuration (broker, backend, timeouts)
- `app/models.py`: Job model for tracking task state and progress
- `app/tasks/zendesk_tasks.py`: Celery tasks (tag_tickets_async, apply_macro_async)
- `app/jobs/`: Blueprint for job monitoring UI with real-time updates

**Running the System**:
```bash
# Terminal 1: Flask app
flask run

# Terminal 2: Celery worker (required for async jobs)
celery -A celery_app worker --loglevel=info

# Terminal 3: Flower monitoring (optional)
celery -A celery_app flower  # Access at http://localhost:5555
```

### Tool Async Support

Tools indicate async support by:
1. Override `supports_async()` to return True
2. Override `get_ticket_limit(async_mode)` to set limits (500 sync, 50000 async)
3. Implement `execute_async(form_data, job_id)` method that:
   - Fetches tickets
   - Creates Job record
   - Dispatches Celery task
   - Returns job info (not results)

Tool routes automatically determine sync vs async based on ticket count and dry-run flag.

## Important Notes

- Tool registration happens on import, so `app/tools/implementations/__init__.py` must import all tool classes
- The `run.py` imports all tool implementations to trigger registration: `from app.tools.implementations import *`
- Zendesk API rate limits should be considered for bulk operations (1 ticket/second with rate limit retry logic)
- Results are stored in session (sync) or Job model (async) to enable export functionality
- CSRF protection is enabled via Flask-WTF for all forms
- Redis must be running for async jobs to work
- Celery worker must be running for background job processing
- Job progress persists across server restarts (stored in database)

### Starting Large Tasks

When exiting plan mode with an accepted plan: 1.**Create Task Directory**:
mkdir -p ~/git/project/dev/active/[task-name]/

2.**Create Documents**:

- `[task-name]-plan.md` - The accepted plan
- `[task-name]-context.md` - Key files, decisions
- `[task-name]-tasks.md` - Checklist of work

3.**Update Regularly**: Mark tasks complete immediately

### Continuing Tasks

- Check `/dev/active/` for existing tasks
- Read all three files before proceeding
- Update "Last Updated" timestamps