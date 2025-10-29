# Async Tag Manager Implementation Plan

**Created**: 2025-10-29
**Last Updated**: 2025-10-29
**Status**: In Progress

## Objective
Implement a Tag Manager tool that can handle bulk tagging operations on 10,000+ tickets using Celery + Redis for asynchronous processing with real-time progress tracking.

## Implementation Phases

### Phase 1: Setup Async Infrastructure (Celery + Redis)

1. **Install dependencies**:
   - Add to `requirements.txt`: celery, redis, flower (for monitoring)

2. **Create Celery configuration** (`app/celery_config.py`):
   - Configure Celery with Redis broker
   - Set task serializer, result backend
   - Configure task time limits and retry policies

3. **Create Celery app** (`celery_app.py` in root):
   - Initialize Celery with Flask app context
   - Import tasks module

4. **Create Job model** (`app/models.py`):
   - Add Job table: id, job_id (Celery task ID), tool_slug, status, progress, result, error, created_at, completed_at, user_id
   - Methods: create_job(), update_status(), get_results()

5. **Database migration**:
   - `flask db migrate -m "Add Job model for async tasks"`
   - `flask db upgrade`

### Phase 2: Build Task Infrastructure

6. **Create Celery tasks module** (`app/tasks/__init__.py` and `app/tasks/zendesk_tasks.py`):
   - `@shared_task` for tag_tickets_async(job_id, ticket_ids, tags, operation)
   - `@shared_task` for apply_macro_async(job_id, ticket_ids, macro_id)
   - Tasks update Job model with progress every 10-50 tickets
   - Full error handling and rate limiting

7. **Create helper functions** in `app/zendesk/helpers.py`:
   - `add_tags_to_tickets(ticket_ids, tags, delay, progress_callback)`
   - `remove_tags_from_tickets(ticket_ids, tags, delay, progress_callback)`
   - Accept optional callback for progress updates

8. **Update BaseTool** (`app/tools/base_tool.py`):
   - Add `supports_async()` method (already exists, ensure it's used)
   - Add `execute_async(form_data, job_id)` optional method
   - Add `get_ticket_limit()` method (default 500 sync, 50000 async)

### Phase 3: Build Job Monitoring UI

9. **Create jobs blueprint** (`app/jobs/`):
   - Routes: `/jobs` (list), `/jobs/<job_id>` (status), `/jobs/<job_id>/cancel`
   - Job list page with filters (status, tool, date)
   - Job status page with real-time progress (AJAX polling every 2 seconds)
   - Cancel/retry functionality

10. **Create templates**:
    - `templates/jobs/list.html` - List all jobs
    - `templates/jobs/status.html` - Real-time job status with progress bar
    - Update `base.html` to add Jobs link in navbar

### Phase 4: Implement Tag Manager Tool

11. **Create Tag Manager** (`app/tools/implementations/tag_manager.py`):
    - Metadata: name="Tag Manager", slug="tag-manager", requires_admin=False
    - Form fields: view dropdown, operation (add/remove), tags input, ticket limit (max 50000), dry run checkbox
    - `supports_async()` returns True
    - `execute()` for sync/dry-run (≤500 tickets)
    - `execute_async()` creates Job record and dispatches Celery task for >500 tickets
    - Export formats: CSV, JSON

12. **Update tool routes** (`app/tools/routes.py`):
    - Check if tool supports async and ticket count >500
    - If async: create Job, redirect to job status page
    - If sync: execute normally as before

13. **Register tool** in `app/tools/implementations/__init__.py`

### Phase 5: Documentation & Testing

14. **Create startup documentation**:
    - Update README.md with Redis/Celery setup instructions
    - Add commands: `redis-server`, `celery -A celery_app worker --loglevel=info`
    - Optional: Docker Compose for Redis + Celery + Flask

15. **Test end-to-end**:
    - Small job (100 tickets, sync)
    - Large job (1000+ tickets, async)
    - Job cancellation
    - Error handling
    - Progress tracking accuracy

## Expected Outcome
- Celery + Redis infrastructure for background jobs
- Job tracking database and monitoring UI
- Tag Manager tool that handles 10,000+ tickets asynchronously
- Real-time progress tracking
- Foundation for making other tools async (Apply Macro, future tools)
