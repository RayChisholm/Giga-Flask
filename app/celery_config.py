import os


class CeleryConfig:
    """Celery configuration"""

    # Broker settings
    broker_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    result_backend = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

    # Serialization settings
    task_serializer = 'json'
    result_serializer = 'json'
    accept_content = ['json']
    timezone = 'UTC'
    enable_utc = True

    # Task execution settings
    task_track_started = True
    task_time_limit = 3600 * 4  # 4 hours max for a task
    task_soft_time_limit = 3600 * 3  # 3 hours soft limit

    # Worker settings
    worker_prefetch_multiplier = 1  # Process one task at a time
    worker_max_tasks_per_child = 1000  # Restart worker after 1000 tasks (memory management)

    # Result backend settings
    result_expires = 3600 * 24  # Results expire after 24 hours

    # Task routing (can be expanded for different queues)
    task_routes = {
        'app.tasks.zendesk_tasks.*': {'queue': 'zendesk'},
    }

    # Default queue
    task_default_queue = 'celery'
    task_default_exchange = 'celery'
    task_default_routing_key = 'celery'
