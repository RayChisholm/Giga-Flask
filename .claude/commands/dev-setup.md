
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