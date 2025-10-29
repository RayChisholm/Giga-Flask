"""
Routes for job monitoring and management.
"""

from flask import render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app.jobs import jobs_bp
from app.models import Job
from celery.result import AsyncResult


@jobs_bp.route('/')
@login_required
def index():
    """
    Display list of all jobs for the current user.
    """
    # Get filter parameters
    status_filter = request.args.get('status', 'all')
    tool_filter = request.args.get('tool', 'all')
    page = request.args.get('page', 1, type=int)
    per_page = 20

    # Build query
    query = Job.query.filter_by(user_id=current_user.id)

    # Apply filters
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)

    if tool_filter != 'all':
        query = query.filter_by(tool_slug=tool_filter)

    # Order by created date (newest first) and paginate
    jobs = query.order_by(Job.created_at.desc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    # Get unique tool slugs for filter dropdown
    tool_slugs = Job.query.with_entities(Job.tool_slug).distinct().all()
    tool_slugs = [slug[0] for slug in tool_slugs]

    return render_template(
        'jobs/list.html',
        jobs=jobs,
        status_filter=status_filter,
        tool_filter=tool_filter,
        tool_slugs=tool_slugs,
        title='Background Jobs'
    )


@jobs_bp.route('/<int:job_id>')
@login_required
def view_job(job_id):
    """
    Display detailed status of a specific job.
    """
    job = Job.query.get_or_404(job_id)

    # Check if user owns this job
    if job.user_id != current_user.id:
        flash('You do not have permission to view this job.', 'danger')
        return redirect(url_for('jobs.index'))

    return render_template(
        'jobs/status.html',
        job=job,
        title=f'Job {job.id}'
    )


@jobs_bp.route('/<int:job_id>/status')
@login_required
def job_status_api(job_id):
    """
    API endpoint for getting job status (for AJAX polling).
    Returns JSON with current job status.
    """
    job = Job.query.get_or_404(job_id)

    # Check if user owns this job
    if job.user_id != current_user.id:
        return jsonify({'error': 'Permission denied'}), 403

    return jsonify({
        'id': job.id,
        'job_id': job.job_id,
        'tool_slug': job.tool_slug,
        'status': job.status,
        'progress': job.progress,
        'total_items': job.total_items,
        'processed_items': job.processed_items,
        'error_message': job.error_message,
        'elapsed_time': job.get_elapsed_time(),
        'created_at': job.created_at.isoformat(),
        'started_at': job.started_at.isoformat() if job.started_at else None,
        'completed_at': job.completed_at.isoformat() if job.completed_at else None,
        'result': job.get_result()
    })


@jobs_bp.route('/<int:job_id>/cancel', methods=['POST'])
@login_required
def cancel_job(job_id):
    """
    Cancel a running job.
    """
    job = Job.query.get_or_404(job_id)

    # Check if user owns this job
    if job.user_id != current_user.id:
        flash('You do not have permission to cancel this job.', 'danger')
        return redirect(url_for('jobs.index'))

    # Check if job can be cancelled
    if job.status in ['completed', 'failed', 'cancelled']:
        flash(f'Job is already {job.status} and cannot be cancelled.', 'warning')
        return redirect(url_for('jobs.view_job', job_id=job_id))

    try:
        # Import celery here to avoid circular imports
        from celery_app import celery

        # Revoke the Celery task
        celery.control.revoke(job.job_id, terminate=True)

        # Update job status in database
        job.cancel()

        flash(f'Job #{job.id} has been cancelled.', 'success')
    except Exception as e:
        flash(f'Error cancelling job: {str(e)}', 'danger')

    return redirect(url_for('jobs.view_job', job_id=job_id))


@jobs_bp.route('/<int:job_id>/delete', methods=['POST'])
@login_required
def delete_job(job_id):
    """
    Delete a job record (only completed/failed/cancelled jobs).
    """
    job = Job.query.get_or_404(job_id)

    # Check if user owns this job
    if job.user_id != current_user.id:
        flash('You do not have permission to delete this job.', 'danger')
        return redirect(url_for('jobs.index'))

    # Check if job can be deleted
    if job.status in ['pending', 'running']:
        flash('Cannot delete a running job. Please cancel it first.', 'warning')
        return redirect(url_for('jobs.view_job', job_id=job_id))

    try:
        from app import db
        db.session.delete(job)
        db.session.commit()
        flash(f'Job #{job_id} has been deleted.', 'success')
    except Exception as e:
        flash(f'Error deleting job: {str(e)}', 'danger')

    return redirect(url_for('jobs.index'))
