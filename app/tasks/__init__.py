"""
Celery tasks module for asynchronous job processing.
"""

from app.tasks import zendesk_tasks

__all__ = ['zendesk_tasks']
