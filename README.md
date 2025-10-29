# Zendesk Bulk Operations Tool

A Flask web application for performing bulk operations and searches on Zendesk data, with a scalable architecture for easily adding new tools.

## Features

- **Scalable Tool System**: Easy to add new tools by inheriting from `BaseTool`
- **Async Job Processing**: Handle 10,000+ tickets with Celery + Redis background jobs
- **Real-time Progress Tracking**: Monitor long-running jobs with live progress updates
- **User Authentication**: Session-based authentication with role management
- **Admin Panel**: Manage users and Zendesk credentials
- **Bootstrap 5 UI**: Modern, responsive interface
- **Zendesk Integration**: Built on zenpy for robust API access

## Current Tools

1. **Search Macros**: Find macros containing a substring in any of their actions
2. **Apply Macro to View**: Apply a macro to all tickets in a view (up to 500 tickets)
3. **Tag Manager**: Add or remove tags from tickets in bulk (supports up to 50,000 tickets with async processing)

## Quick Start

### Prerequisites

- Python 3.8 or higher
- Zendesk account with API access
- Redis server (for async job processing)

### Installation

1. **Clone or navigate to the project directory**

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   - The `.env` file is already created with default values
   - You can optionally add Zendesk credentials here or configure them in the admin panel later

5. **Install and start Redis** (for background job processing)

   **macOS (using Homebrew):**
   ```bash
   brew install redis
   brew services start redis
   ```

   **Linux (Ubuntu/Debian):**
   ```bash
   sudo apt-get install redis-server
   sudo systemctl start redis-server
   ```

   **Windows:**
   - Download Redis from https://redis.io/download
   - Or use Windows Subsystem for Linux (WSL)

   **Verify Redis is running:**
   ```bash
   redis-cli ping
   # Should return: PONG
   ```

6. **Initialize the database**
   ```bash
   flask init-db
   ```

7. **Create an admin user**
   ```bash
   flask create-admin
   ```
   Follow the prompts to create your first admin user.

8. **Run the application** (requires 3 terminal windows)

   **Terminal 1 - Flask app:**
   ```bash
   source venv/bin/activate
   flask run
   ```

   **Terminal 2 - Celery worker:**
   ```bash
   source venv/bin/activate
   celery -A celery_app worker --loglevel=info
   ```

   **Terminal 3 - Flower (optional, for monitoring):**
   ```bash
   source venv/bin/activate
   celery -A celery_app flower
   # Access at http://localhost:5555
   ```

9. **Access the application**
   - Open your browser to `http://127.0.0.1:5000`
   - Log in with your admin credentials
   - Go to Admin > Zendesk Configuration to set up API credentials

## Project Structure

```
├── app/
│   ├── __init__.py           # App factory
│   ├── config.py             # Configuration
│   ├── models.py             # Database models
│   │
│   ├── auth/                 # Authentication
│   ├── admin/                # Admin panel
│   ├── main/                 # Main pages
│   │
│   ├── tools/                # Tool system
│   │   ├── base_tool.py      # Abstract base class
│   │   ├── registry.py       # Auto-discovery
│   │   ├── routes.py         # Generic routes
│   │   └── implementations/  # Individual tools
│   │
│   ├── zendesk/              # Zendesk integration
│   │   ├── client.py         # Client manager
│   │   └── helpers.py        # Common operations
│   │
│   └── templates/            # HTML templates
│
├── instance/                 # Instance files (gitignored)
├── migrations/               # Database migrations
├── .env                      # Environment variables
├── requirements.txt          # Dependencies
├── run.py                    # Entry point
└── PROJECT_PLAN.md          # Detailed project plan
```

## Adding a New Tool

Adding a new tool is simple! Just create a new file in `app/tools/implementations/`:

```python
from app.tools.base_tool import BaseTool
from app.tools.registry import ToolRegistry

@ToolRegistry.register
class MyNewTool(BaseTool):
    name = "My New Tool"
    slug = "my-new-tool"
    description = "What this tool does"
    category = "Category Name"
    requires_admin = False  # Set to True for admin-only

    def get_form_fields(self):
        return [
            {
                'name': 'input_field',
                'label': 'Input Label',
                'type': 'text',
                'required': True,
                'placeholder': 'Enter something...',
                'help_text': 'Help text here'
            }
        ]

    def validate_input(self, form_data):
        # Validate the input
        if not form_data.get('input_field'):
            return False, "Input field is required"
        return True, None

    def execute(self, form_data):
        # Execute the tool logic
        try:
            # Your logic here
            return {
                'success': True,
                'message': 'Tool executed successfully!',
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

That's it! Your tool will automatically appear in the dashboard.

## Zendesk Setup

1. Log into your Zendesk account
2. Go to Admin Center > Apps and integrations > APIs > Zendesk API
3. Click "Add API token"
4. Copy the generated token
5. In the app, go to Admin > Zendesk Configuration
6. Enter your subdomain, email, and API token
7. Click "Test Connection" to verify

## Configuration

### Environment Variables

Edit `.env` to customize:

- `FLASK_ENV`: `development` or `production`
- `SECRET_KEY`: Change this for production!
- `DATABASE_URL`: SQLite by default
- `REDIS_URL`: Redis connection string (default: `redis://localhost:6379/0`)
- `ZENDESK_*`: Optional, can be set in admin panel

## Async Job Processing

For operations on large datasets (>500 tickets), the application automatically uses background job processing:

### How It Works

1. **Small Jobs (≤500 tickets)**: Execute synchronously, results appear immediately
2. **Large Jobs (>500 tickets)**: Dispatch to Celery, process in background
3. **Dry Run**: Always executes synchronously regardless of size

### Monitoring Jobs

- Navigate to **Jobs** in the navbar to see all your background jobs
- Click on a job to see real-time progress updates
- Progress updates every 2 seconds via AJAX polling
- View detailed results when job completes

### Job Management

- **Cancel**: Stop a running job (pending or in-progress)
- **Delete**: Remove completed/failed job records
- **Export**: Download results as CSV or JSON (when available)

### Performance Notes

- Processing rate: ~1 ticket/second (with rate limiting)
- 1,000 tickets ≈ 17 minutes
- 10,000 tickets ≈ 2.8 hours
- Jobs survive server restarts (stored in database)
- Celery worker must be running for background jobs to process

### Database Migrations

If you modify models:

```bash
flask db migrate -m "Description of changes"
flask db upgrade
```

## Security Notes

- Change the `SECRET_KEY` in production
- Never commit `.env` to version control
- API tokens are stored in the database (consider encryption for production)
- Use HTTPS in production

## Development Commands

```bash
# Initialize database
flask init-db

# Create admin user
flask create-admin

# Run development server
flask run

# Run Celery worker
celery -A celery_app worker --loglevel=info

# Run Flower monitoring (optional)
celery -A celery_app flower

# Access Flask shell with context
flask shell

# Database migrations
flask db migrate -m "message"
flask db upgrade

# Check Redis status
redis-cli ping
```

## Troubleshooting

**Issue**: Database not found
- **Solution**: Run `flask init-db`

**Issue**: No tools showing up
- **Solution**: Make sure tool implementations are imported in `app/tools/implementations/__init__.py`

**Issue**: Zendesk connection fails
- **Solution**: Verify your subdomain, email, and API token are correct. Use "Test Connection" in admin panel.

**Issue**: Import errors
- **Solution**: Make sure virtual environment is activated and dependencies are installed

**Issue**: Celery worker not starting
- **Solution**:
  - Check Redis is running: `redis-cli ping`
  - Verify Redis URL in `.env`
  - Check for port conflicts (Redis default: 6379)
  - Try: `celery -A celery_app worker --loglevel=debug` for detailed logs

**Issue**: Background jobs stuck in "pending" status
- **Solution**:
  - Ensure Celery worker is running
  - Check Celery worker logs for errors
  - Verify Redis connection
  - Restart Celery worker

**Issue**: Jobs failing with connection errors
- **Solution**:
  - Check Zendesk API credentials
  - Verify network connectivity
  - Check for rate limiting (429 errors)
  - Review error messages in job details

**Issue**: Redis connection refused
- **Solution**:
  - Start Redis: `brew services start redis` (macOS) or `sudo systemctl start redis-server` (Linux)
  - Check Redis port: `redis-cli -p 6379 ping`
  - Verify REDIS_URL in environment

## Future Enhancements

See `PROJECT_PLAN.md` for the complete roadmap. Planned features include:

- Apply macros to view tickets
- Bulk tag management
- Ticket deletion tools
- Advanced search within tickets
- Async task processing
- Export functionality
- And many more!

## Contributing

When adding new tools:
1. Follow the `BaseTool` interface
2. Add proper error handling
3. Include helpful form field descriptions
4. Test with your Zendesk instance

## License

This project is for internal use. Modify as needed for your organization.

## Support

For issues or questions, refer to:
- `PROJECT_PLAN.md` for architectural details
- Flask documentation: https://flask.palletsprojects.com/
- Zenpy documentation: https://github.com/facetoe/zenpy
- Zendesk API docs: https://developer.zendesk.com/api-reference/

---

Built with Flask, Bootstrap 5, and zenpy.
