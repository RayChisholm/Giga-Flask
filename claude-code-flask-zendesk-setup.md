# Claude Code Setup Guide: Flask + Zendesk API Project

## Table of Contents
1. [Initial Setup](#initial-setup)
2. [CLAUDE.MD File Structure](#claudemd-file-structure)
3. [Custom Slash Commands](#custom-slash-commands)
4. [Workflow Optimization](#workflow-optimization)
5. [Best Practices](#best-practices)

---

## Initial Setup

### 1. Install Claude Code
```bash
npm install -g @anthropic-ai/claude-code
```

### 2. Initialize Your Project
```bash
cd your-flask-zendesk-project
claude /init
```

This creates a `CLAUDE.md` file that Claude reads every session.

### 3. Create Command Directories
```bash
# Project-specific commands (shared with team via git)
mkdir -p .claude/commands

# Personal commands (just for you)
mkdir -p ~/.claude/commands
```

---

## CLAUDE.MD File Structure

Create a comprehensive `CLAUDE.md` in your project root. Here's a tailored template for your Flask/Zendesk API project:

```markdown
# Flask Zendesk Tools Application

## Project Overview
Multi-tenant Flask application providing internal tools that integrate with Zendesk API. Users authenticate via SSO and access various utility tools for ticket management, reporting, and automation.

## Tech Stack
- **Backend**: Flask 3.x, Python 3.11+
- **API Integration**: Zendesk API (REST)
- **Database**: PostgreSQL (via SQLAlchemy)
- **Authentication**: Flask-Login + SSO (specify your provider)
- **Frontend**: Jinja2 templates, Bootstrap 5
- **Deployment**: Docker, AWS/GCP (specify)

## Project Structure
```
project/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── models/              # SQLAlchemy models
│   ├── routes/              # Blueprint routes
│   ├── services/            # Business logic
│   │   └── zendesk/         # Zendesk API integration
│   ├── templates/           # Jinja2 templates
│   ├── static/              # CSS, JS, images
│   └── utils/               # Helper functions
├── tests/
├── migrations/              # Alembic migrations
├── config.py               # Configuration
├── requirements.txt
└── docker-compose.yml
```

## Coding Standards

### Python Style
- Follow PEP 8
- Use type hints for all function signatures
- Maximum line length: 100 characters
- Use docstrings (Google style) for all classes and functions
- Use f-strings for string formatting

### Flask Conventions
- Use Blueprints for route organization
- Keep routes thin - delegate to service layer
- Use Flask-SQLAlchemy for database operations
- Handle errors with custom error handlers
- Use environment variables for configuration (never hardcode secrets)

### Zendesk API Guidelines
- Always use connection pooling
- Implement retry logic with exponential backoff
- Cache API responses where appropriate (Redis)
- Use Zendesk API v2
- Rate limit: 400 requests/minute (implement throttling)
- Always validate and sanitize Zendesk data before database storage

### Testing Requirements
- Minimum 80% code coverage
- Use pytest for all tests
- Mock Zendesk API calls in tests
- Test fixtures in `tests/conftest.py`
- Integration tests for critical paths

### Security
- Never log sensitive data (API keys, tokens, PII)
- Validate all user inputs
- Use parameterized queries (SQLAlchemy handles this)
- Implement CSRF protection
- Use secure session cookies

## Database Schema Conventions
- Use snake_case for table and column names
- Always include `created_at` and `updated_at` timestamps
- Use UUID for primary keys where appropriate
- Foreign key constraints always enabled
- Index frequently queried columns

## Error Handling
```python
# Standard error response format
{
    "error": {
        "message": "User-friendly message",
        "code": "ERROR_CODE",
        "details": {}  # Optional debug info
    }
}
```

## Environment Variables
Required environment variables in `.env`:
- `FLASK_ENV` - development/production
- `SECRET_KEY` - Flask secret key
- `DATABASE_URL` - PostgreSQL connection string
- `ZENDESK_SUBDOMAIN` - Your Zendesk subdomain
- `ZENDESK_EMAIL` - API user email
- `ZENDESK_API_TOKEN` - API token
- `REDIS_URL` - Redis connection for caching
- `SSO_CLIENT_ID` - SSO client ID
- `SSO_CLIENT_SECRET` - SSO client secret

## Key Workflows

### Adding a New Tool
1. Create route in `app/routes/tools/tool_name.py`
2. Create service in `app/services/tool_name_service.py`
3. Add Zendesk API calls in `app/services/zendesk/`
4. Create template in `app/templates/tools/tool_name.html`
5. Add tests in `tests/test_tool_name.py`
6. Update navigation in base template
7. Add route to Blueprint registration

### Working with Zendesk API
- Always use the service layer abstraction in `app/services/zendesk/`
- Reuse existing API client instances
- Handle rate limiting gracefully
- Log API calls for debugging (without sensitive data)

### Database Migrations
```bash
# Create migration
flask db migrate -m "description"

# Review migration file before applying
# Apply migration
flask db upgrade
```

## Custom Slash Commands
Reference these with natural language or command name:

### Development
- **"/dev-setup"** - Set up development environment
- **"/run-tests"** - Run test suite with coverage
- **"/check-style"** - Run linting and formatting checks

### Zendesk
- **"/zendesk-test"** - Test Zendesk API connection
- **"/zendesk-tool"** - Generate boilerplate for new Zendesk tool

### Deployment
- **"/docker-build"** - Build and test Docker container
- **"/deploy-staging"** - Deploy to staging environment

## Natural Language Triggers
You can say these phrases to trigger workflows:

- **"set up my environment"** → Executes /dev-setup
- **"run the tests"** → Executes /run-tests
- **"create a new tool called [name]"** → Executes /zendesk-tool with argument
- **"test zendesk connection"** → Executes /zendesk-test
- **"check my code"** → Executes /check-style
- **"commit my changes"** → Creates conventional commit and pushes
- **"review my code"** → Performs comprehensive code review

## Important Notes
- Always ask for confirmation before modifying database schema
- Test Zendesk API calls in development environment first
- Never commit `.env` files or API credentials
- Use feature branches for new tools
- Keep dependencies updated monthly
```

---

## Custom Slash Commands

### Project Commands (`.claude/commands/`)

These are shared with your team via git.

#### 1. Development Setup (`dev-setup.md`)

```markdown
# Development Environment Setup

Set up the complete development environment for the Flask Zendesk Tools application.

## Instructions

1. **Check Python Version**
   - Verify Python 3.11+ is installed
   - If not, provide installation instructions

2. **Create Virtual Environment**
   - Create venv: `python -m venv venv`
   - Activate it (OS-specific instructions)

3. **Install Dependencies**
   - Run: `pip install -r requirements.txt`
   - Run: `pip install -r requirements-dev.txt` (for dev dependencies)

4. **Set Up Environment Variables**
   - Copy `.env.example` to `.env`
   - List required variables that need to be filled in
   - Do NOT fill in actual secrets

5. **Database Setup**
   - Ensure PostgreSQL is running
   - Create database if needed
   - Run migrations: `flask db upgrade`

6. **Redis Setup**
   - Verify Redis is running
   - Test connection

7. **Verify Installation**
   - Run test suite: `pytest`
   - Start development server: `flask run`
   - Check health endpoint

8. **Final Checks**
   - List any manual configuration needed
   - Verify all services are running
```

#### 2. Create Zendesk Tool (`zendesk-tool.md`)

```markdown
# Create New Zendesk Tool

Generate complete boilerplate for a new Zendesk-integrated tool.

Tool name: $ARGUMENTS

## Instructions

1. **Gather Requirements**
   - Ask about the tool's purpose
   - Ask what Zendesk endpoints it needs
   - Ask what data it will display/manipulate
   - Ask about authentication requirements

2. **Create Route File**
   - Create `app/routes/tools/$TOOL_NAME.py`
   - Include Blueprint definition
   - Add basic routes (list, detail, create, edit)
   - Include proper error handling
   - Add authentication decorators

3. **Create Service Layer**
   - Create `app/services/$TOOL_NAME_service.py`
   - Implement business logic
   - Add proper error handling
   - Include logging

4. **Create Zendesk Integration**
   - Create or update `app/services/zendesk/$TOOL_NAME_zendesk.py`
   - Implement API calls with retry logic
   - Add rate limiting handling
   - Include caching where appropriate

5. **Create Models** (if needed)
   - Create SQLAlchemy model in `app/models/`
   - Add relationships
   - Create migration file

6. **Create Templates**
   - Create `app/templates/tools/$TOOL_NAME/` directory
   - Create list.html
   - Create detail.html
   - Create form.html (if needed)
   - Extend from base template
   - Include proper CSRF protection

7. **Create Tests**
   - Create `tests/test_$TOOL_NAME.py`
   - Add route tests
   - Add service tests
   - Add Zendesk integration tests (mocked)
   - Aim for 80%+ coverage

8. **Register Blueprint**
   - Add blueprint registration in `app/__init__.py`
   - Add to navigation in base template

9. **Documentation**
   - Add docstrings to all functions
   - Update README if needed
   - Add usage examples

10. **Verification**
    - Run test suite
    - Run linting
    - Manual testing in browser
    - Test error scenarios
```

#### 3. Test Suite Runner (`run-tests.md`)

```markdown
# Run Test Suite

Execute the complete test suite with coverage reporting.

## Instructions

1. **Clean Previous Test Artifacts**
   - Remove `.pytest_cache/`
   - Remove `htmlcov/` if exists
   - Remove `.coverage`

2. **Run Tests with Coverage**
   - Execute: `pytest --cov=app --cov-report=html --cov-report=term-missing`
   - Show verbose output

3. **Analyze Results**
   - Report pass/fail summary
   - Identify files below 80% coverage
   - Highlight any failed tests

4. **Show Coverage Report**
   - Display coverage percentage per file
   - Identify untested code sections
   - Suggest areas needing more tests

5. **Generate HTML Report**
   - Confirm HTML coverage report generated
   - Provide path to open: `htmlcov/index.html`

6. **Recommendations**
   - Suggest specific tests to add
   - Identify risky untested code
```

#### 4. Code Style Check (`check-style.md`)

```markdown
# Code Style and Linting Check

Run all linting and formatting checks for the project.

## Instructions

1. **Black Formatting Check**
   - Run: `black --check app/ tests/`
   - Report files that need formatting
   - If issues found, ask if should auto-fix

2. **isort Import Sorting**
   - Run: `isort --check-only app/ tests/`
   - Report any import sorting issues
   - If issues found, ask if should auto-fix

3. **Flake8 Linting**
   - Run: `flake8 app/ tests/ --max-line-length=100`
   - Report all linting errors
   - Categorize by severity

4. **mypy Type Checking**
   - Run: `mypy app/`
   - Report type errors
   - Suggest fixes for common issues

5. **Security Check**
   - Run: `bandit -r app/`
   - Report security issues
   - Prioritize critical findings

6. **Summary Report**
   - Provide overall pass/fail status
   - List all issues found
   - Suggest running auto-fix if appropriate

7. **Auto-Fix Option**
   - If user confirms, run:
     - `black app/ tests/`
     - `isort app/ tests/`
   - Re-run checks to verify
```

#### 5. Zendesk Connection Test (`zendesk-test.md`)

```markdown
# Test Zendesk API Connection

Verify Zendesk API connectivity and credentials.

## Instructions

1. **Check Environment Variables**
   - Verify ZENDESK_SUBDOMAIN is set
   - Verify ZENDESK_EMAIL is set
   - Verify ZENDESK_API_TOKEN is set
   - Do NOT display the actual values

2. **Test Authentication**
   - Make a simple API call to `/api/v2/users/me.json`
   - Handle authentication errors gracefully
   - Report success or specific error

3. **Test Rate Limiting**
   - Check current rate limit status
   - Report remaining requests
   - Show rate limit reset time

4. **Test Common Endpoints**
   - Test `/api/v2/tickets.json` (list tickets)
   - Test `/api/v2/users.json` (list users)
   - Test `/api/v2/groups.json` (list groups)
   - Report success/failure for each

5. **Connection Quality**
   - Measure response times
   - Check for any warnings in responses
   - Verify API version compatibility

6. **Summary Report**
   - Overall connection status
   - Any issues found
   - Recommendations for fixes

7. **Suggestions**
   - If connection fails, suggest troubleshooting steps
   - If successful, confirm all systems operational
```

#### 6. Docker Build (`docker-build.md`)

```markdown
# Build and Test Docker Container

Build the Docker container and verify it works correctly.

## Instructions

1. **Pre-build Checks**
   - Verify Dockerfile exists
   - Verify docker-compose.yml exists
   - Check for .dockerignore file

2. **Build Container**
   - Run: `docker-compose build`
   - Report build time
   - Show any warnings or errors

3. **Start Services**
   - Run: `docker-compose up -d`
   - Wait for services to be healthy
   - Check logs for errors

4. **Verify Container**
   - Check container is running: `docker-compose ps`
   - Test health endpoint
   - Verify database connection
   - Verify Redis connection

5. **Run Tests in Container**
   - Execute: `docker-compose exec web pytest`
   - Report test results

6. **Check Logs**
   - Show recent logs: `docker-compose logs --tail=50`
   - Identify any errors or warnings

7. **Cleanup Option**
   - Ask if should stop containers
   - Provide cleanup commands if needed

8. **Summary**
   - Report overall success/failure
   - Provide next steps for deployment
```

### Personal Commands (`~/.claude/commands/`)

These are just for you and won't be committed to git.

#### 7. Quick Commit (`commit.md`)

```markdown
# Commit and Push Changes

Create a conventional commit with all changes and push to remote.

## Instructions

1. **Review Changes**
   - Run: `git status`
   - Run: `git diff`
   - Summarize what changed

2. **Determine Commit Type**
   - Analyze changes and select appropriate type:
     - `feat:` - New features
     - `fix:` - Bug fixes
     - `docs:` - Documentation only
     - `style:` - Code formatting
     - `refactor:` - Code restructuring
     - `test:` - Adding tests
     - `chore:` - Maintenance tasks

3. **Stage Changes**
   - Run: `git add -A`

4. **Create Commit**
   - Write descriptive conventional commit message
   - Example: `feat: add ticket bulk update tool`
   - Keep subject line under 72 characters
   - Add body if needed for complex changes

5. **Push Changes**
   - Push to current branch: `git push`
   - Handle any push errors

6. **Confirmation**
   - Report commit hash
   - Confirm push successful
```

#### 8. Quick Review (`quick-review.md`)

```markdown
# Quick Code Review

Perform a focused code review of recent changes.

## Instructions

1. **Identify Changed Files**
   - Run: `git diff --name-only`
   - Focus on files user is currently working on

2. **Code Quality Check**
   - Review for code style consistency
   - Check for proper error handling
   - Verify docstrings are present
   - Check for security issues

3. **Flask-Specific Review**
   - Verify proper Blueprint usage
   - Check route decorators are correct
   - Verify authentication is applied
   - Check for SQL injection risks

4. **Zendesk Integration Review**
   - Verify rate limiting is handled
   - Check for proper error handling
   - Verify sensitive data isn't logged
   - Check for proper retries

5. **Testing Review**
   - Check if tests were added/updated
   - Verify critical paths are tested
   - Check for proper mocking of Zendesk API

6. **Summary Report**
   - List issues found (prioritized)
   - Suggest specific improvements
   - Highlight what was done well
```

---

## Workflow Optimization

### 1. CLAUDE.MD Hierarchical Structure

You can have CLAUDE.MD files at multiple levels:

```
project/
├── CLAUDE.md                    # Project-level (main config)
├── app/
│   ├── services/
│   │   └── zendesk/
│   │       └── CLAUDE.md        # Zendesk-specific guidelines
├── tests/
│   └── CLAUDE.md                # Testing guidelines
```

**Example Zendesk-specific CLAUDE.md** (`app/services/zendesk/CLAUDE.md`):

```markdown
# Zendesk API Integration Guidelines

## Rate Limiting
- Maximum 400 requests per minute
- Implement exponential backoff: start with 1s, double up to 32s
- Always check `X-Rate-Limit-Remaining` header

## Error Handling
Always catch these specific exceptions:
- `429` - Rate limit exceeded (retry with backoff)
- `401` - Authentication failed (check credentials)
- `404` - Resource not found (handle gracefully)
- `500` - Zendesk server error (retry once)

## Caching Strategy
Cache these endpoints for 5 minutes:
- User lists
- Group lists
- Organization lists

Never cache:
- Ticket lists
- Individual ticket details

## API Patterns

### Pagination
```python
def get_all_tickets(self):
    tickets = []
    url = f"{self.base_url}/api/v2/tickets.json"
    
    while url:
        response = self._make_request(url)
        tickets.extend(response['tickets'])
        url = response.get('next_page')
    
    return tickets
```

### Retry Logic
```python
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=32)
)
def _make_request(self, url):
    # Implementation
```
```

### 2. Natural Language Workflow Triggers

Add this section to your main CLAUDE.md to enable natural language:

```markdown
## Work Keywords

When I say these phrases, execute the corresponding command:

- **"set up my environment"** → `/dev-setup`
- **"create a new tool"** or **"new zendesk tool"** → `/zendesk-tool`
- **"run the tests"** or **"test everything"** → `/run-tests`
- **"check my code"** or **"lint this"** → `/check-style`
- **"test zendesk"** or **"check zendesk connection"** → `/zendesk-test`
- **"commit this"** or **"commit my changes"** → `/commit`
- **"quick review"** or **"review my code"** → `/quick-review`
- **"build docker"** or **"build container"** → `/docker-build`
```

### 3. Token Optimization

Instead of loading all instructions in CLAUDE.md, reference slash commands:

```markdown
## Complex Workflows

For complex workflows, use these commands instead of describing them here:

- Creating a new tool: use `/zendesk-tool`
- Setting up environment: use `/dev-setup`
- Running tests: use `/run-tests`

This keeps the CLAUDE.md focused and reduces token usage.
```

### 4. Git Hooks Integration

Add pre-commit hooks to automatically run checks:

```bash
# .git/hooks/pre-commit
#!/bin/bash
claude -p "Run /check-style and report any issues. Block commit if critical issues found."
```

### 5. Continuous Improvement

Add a command to update documentation:

**`update-docs.md`**:
```markdown
# Update Project Documentation

After completing a feature, update relevant documentation.

## Instructions

1. **Review Recent Changes**
   - Check git history for changes made
   - Identify what was added/changed

2. **Update CLAUDE.md**
   - Add any new patterns discovered
   - Update coding standards if changed
   - Add new environment variables if added

3. **Update README**
   - Add new features to feature list
   - Update setup instructions if changed
   - Add new dependencies to prerequisites

4. **Update API Documentation**
   - Document new endpoints
   - Update request/response examples
   - Note any breaking changes

5. **Commit Documentation**
   - Create commit: `docs: update documentation for [feature]`
```

---

## Best Practices

### 1. Start Each Session Right

Begin every Claude Code session with context:

```bash
claude "I'm working on the bulk ticket update feature. Review @app/services/ticket_service.py 
and help me add rate limiting."
```

### 2. Use File References

Reference specific files with `@`:

```bash
claude "Review @app/routes/tickets.py and @tests/test_tickets.py for issues"
```

### 3. Pipe Data In

For logs, errors, or data analysis:

```bash
tail -f logs/app.log | claude "analyze these errors and suggest fixes"
```

### 4. Incremental Development

Break large features into steps:

```bash
claude "Create the database model for bulk ticket operations"
# After reviewing
claude "Now create the service layer for bulk operations"
# After reviewing
claude "Now create the routes and templates"
```

### 5. Regular Code Reviews

Schedule regular reviews:

```bash
# Daily quick review
claude "/quick-review"

# Before merging
claude "Perform comprehensive review of feature/bulk-update branch compared to main"
```

### 6. Documentation-Driven Development

Update docs as you go:

```bash
claude "I just finished the bulk update feature. /update-docs"
```

### 7. Test-Driven Development

Let Claude help with TDD:

```bash
claude "Create tests for bulk ticket update feature first, then implement the feature"
```

### 8. Use Extended Thinking for Complex Problems

For architectural decisions:

```bash
claude --extended-thinking "Design the architecture for a ticket automation engine that 
processes 1000+ tickets per hour with Zendesk API rate limits"
```

### 9. Headless Mode for Automation

Use in CI/CD:

```bash
# In .github/workflows/test.yml
- name: Run AI Code Review
  run: |
    claude -p "Review changed files and comment on PR" \
    --output-format stream-json
```

### 10. Keep Commands Focused

Each slash command should do ONE thing well. Don't create mega-commands.

---

## Quick Reference Card

Save this for easy access:

```
╔══════════════════════════════════════════════════════════╗
║         CLAUDE CODE - FLASK ZENDESK PROJECT             ║
╠══════════════════════════════════════════════════════════╣
║ SETUP                                                    ║
║  /dev-setup          Set up development environment      ║
║  /zendesk-test       Test Zendesk API connection        ║
║                                                          ║
║ DEVELOPMENT                                              ║
║  /zendesk-tool       Create new Zendesk tool           ║
║  /check-style        Lint and format check              ║
║  /run-tests          Run test suite with coverage       ║
║                                                          ║
║ GIT                                                      ║
║  /commit             Smart commit with message          ║
║  /quick-review       Fast code review                   ║
║                                                          ║
║ DEPLOYMENT                                               ║
║  /docker-build       Build and test container           ║
║  /deploy-staging     Deploy to staging                  ║
║                                                          ║
║ NATURAL LANGUAGE                                         ║
║  "set up environment" "run tests" "check code"          ║
║  "create new tool" "commit changes" "review code"       ║
╚══════════════════════════════════════════════════════════╝
```

---

## Next Steps

1. **Create your CLAUDE.md** with the template above (customize for your needs)
2. **Add slash commands** one at a time, starting with most-used workflows
3. **Test each command** to ensure it works as expected
4. **Share with team** - commit `.claude/commands/` to git
5. **Iterate** - improve commands based on usage
6. **Add hooks** for automated workflows
7. **Monitor token usage** - use `claude --debug` to see what's being loaded

---

## Troubleshooting

### Command Not Recognized
- Check file is in `.claude/commands/` (project) or `~/.claude/commands/` (personal)
- Ensure file has `.md` extension
- Restart Claude Code session
- Run `claude /help` to see all available commands

### Command Not Working as Expected
- Check the markdown formatting
- Ensure Instructions section is properly formatted
- Test $ARGUMENTS parameter separately
- Use `claude --debug` to see execution details

### High Token Usage
- Move detailed instructions from CLAUDE.md to slash commands
- Reference commands instead of including full instructions
- Use hierarchical CLAUDE.md files for specific contexts
- Enable the token budget warning

### Zendesk Rate Limiting Issues
- Implement caching in your code
- Add delays between bulk operations
- Use batch endpoints where available
- Monitor rate limit headers in all responses

---

## Additional Resources

- **Official Claude Code Docs**: https://docs.claude.com/en/docs/claude-code/overview
- **Claude Code Best Practices**: https://www.anthropic.com/engineering/claude-code-best-practices
- **Awesome Claude Code**: https://github.com/hesreallyhim/awesome-claude-code
- **ClaudeLog Knowledge Base**: https://claudelog.com/

---

*This guide is specific to Flask + Zendesk API projects. Adjust commands and workflows based on your specific requirements.*
