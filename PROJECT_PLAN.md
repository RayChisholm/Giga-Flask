# Zendesk Bulk Operations Tool - Project Plan

## Overview
A Flask web application for performing bulk operations and searches on Zendesk data, with a scalable architecture for easily adding new tools.

## Core Objectives
1. **Immediate Goals**: ✅ COMPLETE - Flask app running locally with authentication, admin page, landing page, and Zendesk client integration
2. **Long-term Vision**: ✅ COMPLETE - Scalable tool system with async job processing for large-scale operations
3. **Initial Tools**:
   - ✅ Macro search (COMPLETE)
   - ✅ Apply macros to views (COMPLETE - up to 500 tickets)
   - ✅ Tag management (COMPLETE - with async support for 10,000+ tickets)
   - ⏳ Ticket deletion (PLANNED)
   - ⏳ String search in views (PLANNED)

---

## High-Level Architecture

### 1. Application Structure (Modular Blueprint Pattern)
```
giga-flask/
├── app/
│   ├── __init__.py              # App factory
│   ├── config.py                # Configuration classes
│   ├── models.py                # Database models (users, settings)
│   │
│   ├── auth/                    # Authentication blueprint
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── forms.py
│   │
│   ├── admin/                   # Admin panel blueprint
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── forms.py
│   │
│   ├── main/                    # Main pages (landing, dashboard)
│   │   ├── __init__.py
│   │   └── routes.py
│   │
│   ├── tools/                   # Tool system (THE CORE SCALABILITY PIECE)
│   │   ├── __init__.py
│   │   ├── base_tool.py         # Abstract base class for all tools
│   │   ├── registry.py          # Auto-discovery and registration
│   │   ├── routes.py            # Generic tool execution routes
│   │   └── implementations/     # Individual tool implementations
│   │       ├── __init__.py
│   │       ├── macro_search.py
│   │       ├── macro_apply.py
│   │       ├── tag_manager.py
│   │       ├── ticket_delete.py
│   │       └── string_search.py
│   │
│   ├── zendesk/                 # Zendesk integration layer
│   │   ├── __init__.py
│   │   ├── client.py            # Zenpy wrapper/singleton
│   │   └── helpers.py           # Common Zendesk operations
│   │
│   ├── templates/               # Jinja2 templates
│   │   ├── base.html
│   │   ├── auth/
│   │   ├── admin/
│   │   ├── main/
│   │   └── tools/
│   │       ├── tool_base.html   # Generic tool UI template
│   │       └── [custom_templates]/
│   │
│   └── static/                  # CSS, JS, images
│       ├── css/
│       ├── js/
│       └── img/
│
├── migrations/                  # Database migrations (Flask-Migrate)
├── instance/                    # Instance-specific files (gitignored)
│   ├── config.py               # Local config overrides
│   └── app.db                  # SQLite database
├── tests/
├── .env                        # Environment variables (gitignored)
├── .env.example                # Template for environment variables
├── requirements.txt
├── run.py                      # Application entry point
└── README.md
```

---

## Technical Stack

### Core Dependencies
- **Flask**: Web framework
- **Flask-Login**: User session management
- **Flask-SQLAlchemy**: ORM for database
- **Flask-Migrate**: Database migrations
- **Flask-WTF**: Form handling and CSRF protection
- **zenpy**: Zendesk API client
- **python-dotenv**: Environment variable management

### Database
- **SQLite** (development/local): Simple, no setup required
- **PostgreSQL** (future production): If deployed to cloud

---

## Key Components Design

### 1. Authentication System
**Approach**: Session-based authentication with Flask-Login

**Features**:
- Login/logout functionality
- User roles: Admin, Standard User
- Password hashing (bcrypt or werkzeug.security)
- Session management
- Protected routes decorator

**Database Schema**:
```
User
- id: Integer (PK)
- username: String (unique)
- email: String (unique)
- password_hash: String
- role: String (admin/user)
- created_at: DateTime
- active: Boolean
```

### 2. Admin Panel
**Purpose**: Manage application settings and Zendesk configuration

**Features**:
- Zendesk API credential management (subdomain, email, API token)
- User management (create/edit/delete users)
- View registered tools
- Application settings
- Test Zendesk connection

**Security**: Only accessible to admin role users

### 3. Zendesk Integration Layer

**Design Pattern**: Singleton/Factory pattern for client management

**Key Components**:
```python
# app/zendesk/client.py
class ZendeskClientManager:
    """Singleton that manages zenpy client instances"""
    - get_client() -> Zenpy
    - test_connection() -> bool
    - refresh_credentials()
```

**Configuration Storage**:
- Store credentials in database (encrypted) OR environment variables
- Allow admin panel to update credentials
- Validate credentials before storing

**Error Handling**:
- Graceful handling of API rate limits
- Connection failures
- Authentication errors
- Informative error messages to users

### 4. Tool System (SCALABILITY CORE)

**Design Pattern**: Plugin architecture with abstract base class

**Base Tool Interface**:
```python
# app/tools/base_tool.py
class BaseTool(ABC):
    """Abstract base class that all tools must inherit from"""

    # Class attributes (metadata)
    name: str                    # Display name
    slug: str                    # URL-safe identifier
    description: str             # What the tool does
    category: str                # For grouping tools
    requires_admin: bool = False # Permission level

    # Abstract methods (must be implemented)
    @abstractmethod
    def render_form(self) -> str:
        """Return HTML form for tool input"""
        pass

    @abstractmethod
    def execute(self, form_data: dict) -> dict:
        """Execute the tool logic, return results"""
        pass

    @abstractmethod
    def validate_input(self, form_data: dict) -> tuple[bool, str]:
        """Validate form input, return (valid, error_message)"""
        pass

    # Optional methods
    def get_template(self) -> str:
        """Return custom template path or use default"""
        return 'tools/tool_base.html'

    def supports_async(self) -> bool:
        """Whether tool can run asynchronously"""
        return False
```

**Tool Registry**:
```python
# app/tools/registry.py
class ToolRegistry:
    """Auto-discovers and registers all tools"""

    _tools = {}

    @classmethod
    def register(cls, tool_class):
        """Decorator to register a tool"""
        cls._tools[tool_class.slug] = tool_class
        return tool_class

    @classmethod
    def get_tool(cls, slug) -> BaseTool:
        """Get tool instance by slug"""
        pass

    @classmethod
    def get_all_tools(cls) -> dict:
        """Get all registered tools"""
        pass

    @classmethod
    def get_tools_by_category(cls, category) -> list:
        """Get tools grouped by category"""
        pass
```

**Example Tool Implementation**:
```python
# app/tools/implementations/macro_search.py
from app.tools.base_tool import BaseTool
from app.tools.registry import ToolRegistry

@ToolRegistry.register
class MacroSearchTool(BaseTool):
    name = "Search Macros"
    slug = "macro-search"
    description = "Find macros containing a substring in any action"
    category = "Macros"

    def render_form(self):
        # Return form HTML or use WTForms
        pass

    def execute(self, form_data):
        # Implementation using Zendesk client
        search_term = form_data.get('search_term')
        client = get_zendesk_client()
        # ... search logic ...
        return {'results': [...], 'count': 10}

    def validate_input(self, form_data):
        if not form_data.get('search_term'):
            return False, "Search term is required"
        return True, ""
```

**Generic Tool Routes**:
```python
# app/tools/routes.py
@tools_bp.route('/tools/<slug>', methods=['GET', 'POST'])
@login_required
def execute_tool(slug):
    """Generic route that works for all registered tools"""
    tool = ToolRegistry.get_tool(slug)

    if request.method == 'POST':
        valid, error = tool.validate_input(request.form)
        if valid:
            results = tool.execute(request.form)
            return render_template(tool.get_template(),
                                   tool=tool, results=results)

    return render_template(tool.get_template(), tool=tool)
```

**Benefits**:
- **Easy to add tools**: Create new file, inherit from BaseTool, implement methods
- **No route changes**: Generic routes handle all tools
- **Consistent UI**: Shared template structure
- **Automatic registration**: Registry decorator handles discovery
- **Type safety**: Abstract base class enforces interface

---

## Initial Tool Set

### 1. Macro Search Tool
- **Input**: Search substring
- **Process**: Fetch all macros, search in actions field
- **Output**: List of matching macros with highlighted matches

### 2. Apply Macro to View
- **Input**: View ID/name, Macro ID/name
- **Process**: Get all tickets in view, apply macro to each
- **Output**: Progress indicator, success/failure count
- **Considerations**: Rate limiting, batch processing, async operation

### 3. Tag Manager for Views
- **Input**: View ID, tags to add/remove, operation type
- **Process**: Get all tickets in view, update tags
- **Output**: Tickets updated count, any errors

### 4. Delete Tickets in View
- **Input**: View ID, confirmation checkbox
- **Process**: Get tickets, delete each (with safety checks)
- **Output**: Deletion count, errors
- **Safety**: Multiple confirmations, admin-only

### 5. String Search in View
- **Input**: View ID, search string, fields to search
- **Process**: Iterate tickets, search in specified fields
- **Output**: Matching tickets with context

---

## Page Structure

### Landing Page (Dashboard)
- **Route**: `/`
- **Content**:
  - Welcome message
  - Tool categories/grid
  - Quick stats (if applicable)
  - Recent activity (future)
- **Access**: Authenticated users only

### Admin Panel
- **Route**: `/admin`
- **Sections**:
  - Zendesk Configuration
  - User Management
  - Registered Tools List
  - System Settings
  - Connection Test
- **Access**: Admin role only

### Tool Pages
- **Route**: `/tools/<slug>`
- **Layout**:
  - Tool name and description
  - Input form
  - Execute button
  - Results section (dynamic)
  - Export options (CSV, JSON)
- **Access**: Based on tool's `requires_admin` flag

---

## Development Phases

### Phase 1: Foundation (MVP for local testing)
**Goal**: Get basic app running with one working tool

1. **Setup**
   - Initialize Flask project structure
   - Install dependencies
   - Create configuration system
   - Setup .env file for secrets

2. **Database**
   - Create User model
   - Create Settings model (for Zendesk config)
   - Initialize SQLAlchemy
   - Setup Flask-Migrate
   - Create initial migration

3. **Authentication**
   - Implement login/logout
   - Create basic user management
   - Setup Flask-Login
   - Create login template
   - Add protected route decorator

4. **Zendesk Client**
   - Create client wrapper
   - Setup credential management
   - Test connection functionality
   - Error handling

5. **Basic Pages**
   - Landing page template
   - Admin page template
   - Base template with navigation

6. **Tool System Foundation**
   - Create BaseTool abstract class
   - Create ToolRegistry
   - Setup generic tool routes
   - Create base tool template

7. **First Tool**
   - Implement Macro Search tool
   - Test end-to-end
   - Refine tool interface based on learnings

### Phase 2: Core Tools
**Goal**: Implement all initial tools

1. Apply Macro to View
2. Tag Manager
3. Delete Tickets (with safety)
4. String Search in View

### Phase 3: Enhancement
**Goal**: Improve UX and add features

1. Async task processing (Celery or similar)
2. Progress indicators for long-running tasks
3. Export functionality (CSV, JSON)
4. Error logging and display
5. Tool usage analytics
6. Improved UI/styling (Bootstrap or Tailwind)

### Phase 4: Production Readiness (Future)
1. PostgreSQL migration
2. Docker containerization
3. Environment-based configuration
4. Comprehensive testing
5. Deployment documentation
6. Backup/restore functionality

---

## Configuration Management

### Environment Variables (.env)
```
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=<random-secret-key>
DATABASE_URL=sqlite:///instance/app.db

# Zendesk credentials (optional, can be in admin panel)
ZENDESK_SUBDOMAIN=your-subdomain
ZENDESK_EMAIL=your-email@example.com
ZENDESK_TOKEN=your-api-token
```

### Configuration Classes (config.py)
```python
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    # ... other config

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True

class ProductionConfig(Config):
    DEBUG = False
    # ... production settings
```

---

## Security Considerations

1. **Authentication**
   - Strong password requirements
   - Password hashing (never store plaintext)
   - Session timeout
   - CSRF protection (Flask-WTF)

2. **Zendesk Credentials**
   - Never commit to version control
   - Encrypt sensitive data in database
   - Use environment variables when possible
   - Validate credentials before storing

3. **Tool Execution**
   - Input validation for all tools
   - Sanitize user inputs
   - Confirmation dialogs for destructive actions
   - Rate limiting for bulk operations
   - Audit logging for critical operations

4. **Access Control**
   - Role-based access (admin vs user)
   - Tool-level permissions
   - Route protection decorators

---

## Testing Strategy

### Unit Tests
- Tool validation logic
- Zendesk client wrapper
- Authentication functions

### Integration Tests
- Tool execution end-to-end
- Database operations
- API interactions

### Manual Testing Checklist
- [ ] User can log in/out
- [ ] Admin can access admin panel
- [ ] Admin can configure Zendesk credentials
- [ ] Zendesk connection test works
- [ ] Each tool executes successfully
- [ ] Error handling displays properly
- [ ] Bulk operations respect rate limits

---

## Future Enhancements (Post-MVP)

1. **Advanced Features**
   - Scheduled bulk operations
   - Saved searches/templates
   - Operation history and rollback
   - Bulk operation queuing
   - Email notifications on completion
   - Webhook triggers

2. **Additional Tools**
   - User management tools
   - Organization bulk operations
   - Ticket field bulk updates
   - SLA policy analysis
   - Automation rule testing
   - Custom field management
   - Bulk attachment operations

3. **UI/UX**
   - Dark mode
   - Mobile-responsive design
   - Real-time progress updates (WebSockets)
   - Keyboard shortcuts
   - Customizable dashboards

4. **Performance**
   - Caching layer (Redis)
   - Async task queue (Celery)
   - Database query optimization
   - Pagination for large result sets

5. **Deployment**
   - Multi-tenant support
   - Cloud deployment (Heroku, AWS, GCP)
   - CI/CD pipeline
   - Monitoring and alerting

---

## Success Metrics

### Phase 1 Success Criteria
- [ ] Flask app runs locally without errors
- [ ] User can create account and log in
- [ ] Admin can configure Zendesk credentials
- [ ] Zendesk client successfully connects
- [ ] At least one tool (Macro Search) fully functional
- [ ] Clean, navigable UI

### Long-term Success
- Easy to add new tools (< 1 hour per simple tool)
- Stable bulk operations handling 1000+ items
- Fast response times (< 3s for most operations)
- Zero data loss or corruption
- Positive user feedback on usability

---

## Getting Started (Quick Start Commands)

```bash
# Setup virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env with your settings

# Initialize database
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# Create admin user (custom command)
flask create-admin

# Run development server
flask run
```

---

## Questions to Answer During Development

1. Should Zendesk credentials be per-user or application-wide?
2. How should we handle Zendesk API rate limits? (429 responses)
3. Should bulk operations be synchronous or asynchronous?
4. What's the maximum safe batch size for bulk operations?
5. Should we implement operation rollback capabilities?
6. How do we handle partial failures in bulk operations?
7. Should we log all operations for audit purposes?

---

## Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Zenpy Documentation](https://github.com/facetoe/zenpy)
- [Zendesk API Documentation](https://developer.zendesk.com/api-reference/)
- [Flask-Login Documentation](https://flask-login.readthedocs.io/)
- [Flask-SQLAlchemy Documentation](https://flask-sqlalchemy.palletsprojects.com/)

---

## Notes

- **Scalability**: The tool system is the most critical piece - spend time getting the abstraction right
- **Safety**: Implement multiple confirmations and safeguards for destructive operations
- **Rate Limits**: Zendesk API has rate limits - implement throttling and retry logic
- **User Experience**: Bulk operations can take time - provide clear progress feedback
- **Extensibility**: Future tools might need different input types, async processing, scheduling - keep the base class flexible

---

**Last Updated**: 2025-10-29
**Status**: ✅ Phase 1 COMPLETE | ✅ Phase 2 IN PROGRESS (3/5 tools) | ✅ ASYNC SYSTEM DEPLOYED
**Next Step**: Implement remaining tools (Ticket Delete, String Search) or enhance existing tools

---

## 🎉 Recent Updates (2025-10-29)

### Async Job Processing System ✅ DEPLOYED
- **Celery + Redis** integration for background job processing
- **Job Model** added to track async task state and progress
- **Jobs Blueprint** with monitoring UI and real-time progress updates
- **Tag Manager Tool** with support for 10,000+ tickets via async processing
- **Performance**: Handles large-scale operations (tested ready for 50,000 tickets)

### System Architecture Enhancements
- **Jobs Monitoring**: Real-time AJAX-based progress tracking (2-second polling)
- **Async Threshold**: Operations >500 tickets automatically use background processing
- **Rate Limiting**: 1 ticket/second with automatic retry on 429 errors
- **Job Persistence**: Jobs survive server restarts (stored in database)
- **Worker Configuration**: 8 concurrent worker processes via Celery

### New Dependencies
- `celery==5.3.4` - Distributed task queue
- `redis==5.0.1` - Message broker and result backend
- `flower==2.0.1` - Real-time monitoring web UI

### Infrastructure Status
- ✅ Redis server installed and running (Homebrew)
- ✅ Flask application running on port 5000
- ✅ Celery worker running with 2 registered tasks
- ✅ Database migrated with Job table
- ✅ All 3 tools registered and operational

### Current Tools Status
1. **Search Macros** (macro-search) - ✅ COMPLETE
   - Find macros containing substring
   - Export: CSV, JSON

2. **Apply Macro to View** (apply-macro-to-view) - ✅ COMPLETE
   - Apply macros to view tickets (up to 500)
   - Dry-run mode, safety limits
   - Export: CSV, JSON

3. **Tag Manager** (tag-manager) - ✅ COMPLETE + ASYNC
   - Add/remove tags from view tickets
   - Async support for 10,000+ tickets
   - Real-time progress tracking
   - Export: CSV, JSON
   - Max: 50,000 tickets per job