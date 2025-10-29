# Async Tag Manager - Context & Key Decisions

**Created**: 2025-10-29
**Last Updated**: 2025-10-29

## Key Architecture Decisions

### 1. Async Processing Approach
**Decision**: Use Celery + Redis for background job processing
**Rationale**:
- Need to handle 10,000+ tickets (2-3 hours with rate limiting)
- Celery is industry standard, mature, and reliable
- Redis provides fast message broker and result backend
- Enables proper progress tracking and job management
**Alternatives Rejected**:
- Simple background threads (lost on server restart)
- Chunked manual processing (poor UX for large jobs)

### 2. Sync/Async Threshold
**Decision**: Jobs ≤500 tickets run synchronously, >500 run asynchronously
**Rationale**:
- 500 tickets takes ~8-10 minutes (acceptable wait time)
- Reduces complexity for small jobs
- User can see immediate results for small operations

### 3. Progress Tracking
**Decision**: Update Job model every 10-50 tickets processed
**Rationale**:
- Balance between database writes and UX feedback
- Users get meaningful progress updates
- Not too frequent to cause database overhead

## Key Files & Their Roles

### Infrastructure Files
- `celery_app.py`: Celery application initialization with Flask context
- `app/celery_config.py`: Celery configuration (broker, backend, serializers)
- `app/models.py`: Job model for tracking async tasks
- `app/tasks/zendesk_tasks.py`: Celery task definitions

### Tool System Files
- `app/tools/base_tool.py`: Base class with async support methods
- `app/tools/routes.py`: Generic tool routes with async dispatch logic
- `app/tools/implementations/tag_manager.py`: Tag Manager tool implementation

### Job Monitoring Files
- `app/jobs/routes.py`: Job list, status, and control endpoints
- `templates/jobs/status.html`: Real-time progress tracking UI
- `templates/jobs/list.html`: Job history and management

### Helper Files
- `app/zendesk/helpers.py`: Tag manipulation functions with progress callbacks

## Integration Points

### 1. Tool → Job System
- Tool's `execute_async()` creates Job record
- Returns job_id for tracking
- Routes redirect to job status page

### 2. Job → Celery Task
- Job record stores Celery task_id
- Task updates Job.status and Job.progress
- Task stores final results in Job.result

### 3. UI → Job Status
- AJAX polling every 2 seconds
- Fetches job status from database
- Updates progress bar and status message

## Database Schema

### Job Model
```python
- id: Integer (PK)
- job_id: String (Celery task ID, unique, indexed)
- tool_slug: String (which tool created this)
- status: String (pending, running, completed, failed, cancelled)
- progress: Integer (0-100 percentage)
- total_items: Integer (total tickets to process)
- processed_items: Integer (tickets processed so far)
- result: JSON (final results)
- error: Text (error message if failed)
- created_at: DateTime
- completed_at: DateTime
- user_id: Integer (FK to User)
```

## Environment Requirements

### New Dependencies
- `celery>=5.3.0` - Task queue
- `redis>=5.0.0` - Message broker
- `flower>=2.0.0` - Optional monitoring UI

### Runtime Requirements
- Redis server running on localhost:6379
- Celery worker process: `celery -A celery_app worker --loglevel=info`
- Flask app: `flask run`

## Rate Limiting Strategy

- Zendesk API rate limit: ~700 requests/minute
- Tool uses 1 second delay between tickets (conservative)
- 10,000 tickets ≈ 2.8 hours
- Retry logic for 429 rate limit responses (wait 60 seconds, retry once)

## Future Enhancements
- Flower dashboard integration for admin monitoring
- Email notifications on job completion
- Job scheduling (run at specific time)
- Job templates (save common operations)
- Batch job queueing (process multiple views)
