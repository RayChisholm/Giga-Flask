"""
Celery tasks for Zendesk bulk operations.

These tasks run asynchronously in the background, updating job progress
as they process tickets.
"""

from celery import shared_task
from app import db
from app.models import Job
from app.zendesk.helpers import add_tags_to_tickets, remove_tags_from_tickets, apply_macro_to_tickets
import time


@shared_task(bind=True, name='app.tasks.zendesk_tasks.tag_tickets_async')
def tag_tickets_async(self, job_id, ticket_ids, tags, operation):
    """
    Asynchronously add or remove tags from multiple tickets.

    Args:
        self: Celery task instance (bound)
        job_id: Job ID from database
        ticket_ids: List of ticket IDs to process
        tags: List of tags to add or remove
        operation: 'add' or 'remove'

    Returns:
        Dict with results
    """
    # Get job from database
    job = Job.query.filter_by(job_id=self.request.id).first()
    if not job:
        return {'success': False, 'error': 'Job not found in database'}

    try:
        # Update job status to running
        job.update_progress(0, status='running')

        # Define progress callback
        def progress_callback(processed, total):
            """Update job progress in database"""
            job.update_progress(processed, status='running')

        # Execute the tagging operation
        if operation == 'add':
            results = add_tags_to_tickets(
                ticket_ids=ticket_ids,
                tags=tags,
                delay=1.0,
                progress_callback=progress_callback
            )
        elif operation == 'remove':
            results = remove_tags_from_tickets(
                ticket_ids=ticket_ids,
                tags=tags,
                delay=1.0,
                progress_callback=progress_callback
            )
        else:
            raise ValueError(f"Invalid operation: {operation}")

        # Mark job as complete with results
        job.complete(result_data=results, status='completed')

        return {
            'success': True,
            'operation': operation,
            'tags': tags,
            'results': results
        }

    except Exception as e:
        # Mark job as failed
        error_msg = str(e)
        job.fail(error_msg)

        return {
            'success': False,
            'error': error_msg
        }


@shared_task(bind=True, name='app.tasks.zendesk_tasks.apply_macro_async')
def apply_macro_async(self, job_id, ticket_ids, macro_id):
    """
    Asynchronously apply a macro to multiple tickets.

    This task is for future use when Apply Macro to View tool is upgraded to async.

    Args:
        self: Celery task instance (bound)
        job_id: Job ID from database
        ticket_ids: List of ticket IDs to process
        macro_id: Macro ID to apply

    Returns:
        Dict with results
    """
    # Get job from database
    job = Job.query.filter_by(job_id=self.request.id).first()
    if not job:
        return {'success': False, 'error': 'Job not found in database'}

    try:
        # Update job status to running
        job.update_progress(0, status='running')

        # Define progress callback
        def progress_callback(processed, total):
            """Update job progress in database"""
            job.update_progress(processed, status='running')

        # Apply macro to tickets
        results = apply_macro_to_tickets(
            ticket_ids=ticket_ids,
            macro_id=macro_id,
            delay=1.0,
            progress_callback=progress_callback
        )

        # Mark job as complete with results
        job.complete(result_data=results, status='completed')

        return {
            'success': True,
            'macro_id': macro_id,
            'results': results
        }

    except Exception as e:
        # Mark job as failed
        error_msg = str(e)
        job.fail(error_msg)

        return {
            'success': False,
            'error': error_msg
        }
