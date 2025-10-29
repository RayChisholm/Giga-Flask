from typing import Dict, Tuple, Optional
import csv
import json
from io import StringIO
from app.tools.base_tool import BaseTool
from app.tools.registry import ToolRegistry
from app.zendesk.helpers import (
    get_all_views,
    get_view_tickets,
    add_tags_to_tickets,
    remove_tags_from_tickets
)


@ToolRegistry.register
class TagManagerTool(BaseTool):
    """
    Tool to add or remove tags from all tickets in a Zendesk view.
    Supports asynchronous processing for large datasets (10,000+ tickets).
    """

    name = "Tag Manager"
    slug = "tag-manager"
    description = "Add or remove tags from all tickets in a view (supports up to 50,000 tickets)"
    category = "Tags"
    requires_admin = False

    def get_form_fields(self) -> list:
        """Define the form fields for this tool."""
        try:
            # Fetch views for dropdown
            views = get_all_views()
            view_options = [
                {
                    'value': str(view.id),
                    'label': f"{view.title} (ID: {view.id})"
                }
                for view in views
            ]
        except Exception as e:
            view_options = [{'value': 'error', 'label': f'Error loading views: {str(e)}'}]

        return [
            {
                'name': 'view_id',
                'label': 'Select View',
                'type': 'select',
                'required': True,
                'options': view_options,
                'help_text': 'Choose the view containing the tickets you want to update'
            },
            {
                'name': 'operation',
                'label': 'Operation',
                'type': 'select',
                'required': True,
                'options': [
                    {'value': 'add', 'label': 'Add Tags'},
                    {'value': 'remove', 'label': 'Remove Tags'}
                ],
                'help_text': 'Choose whether to add or remove tags'
            },
            {
                'name': 'tags',
                'label': 'Tags',
                'type': 'text',
                'required': True,
                'placeholder': 'tag1, tag2, tag3',
                'help_text': 'Enter tags separated by commas (e.g., "urgent, needs-review, escalated")'
            },
            {
                'name': 'ticket_limit',
                'label': 'Ticket Limit',
                'type': 'number',
                'required': True,
                'placeholder': '500',
                'help_text': 'Maximum number of tickets to process. Up to 500 for immediate results, up to 50,000 for background processing.'
            },
            {
                'name': 'dry_run',
                'label': 'Dry Run (Preview Only)',
                'type': 'checkbox',
                'required': False,
                'help_text': 'Check this to preview which tickets would be affected without making changes'
            }
        ]

    def validate_input(self, form_data: Dict) -> Tuple[bool, Optional[str]]:
        """Validate the form input."""
        view_id = form_data.get('view_id')
        operation = form_data.get('operation')
        tags = form_data.get('tags', '').strip()
        ticket_limit = form_data.get('ticket_limit')

        if not view_id:
            return False, "Please select a view"

        if view_id == 'error':
            return False, "Unable to load views. Please check your Zendesk configuration."

        if not operation or operation not in ['add', 'remove']:
            return False, "Please select a valid operation (add or remove)"

        if not tags:
            return False, "Please enter at least one tag"

        if not ticket_limit:
            return False, "Please specify a ticket limit"

        try:
            limit = int(ticket_limit)
            if limit < 1:
                return False, "Ticket limit must be at least 1"
            if limit > 50000:
                return False, "Ticket limit cannot exceed 50,000. Please process in smaller batches."
        except ValueError:
            return False, "Ticket limit must be a valid number"

        return True, None

    def supports_async(self) -> bool:
        """This tool supports async execution for large datasets."""
        return True

    def get_ticket_limit(self, async_mode: bool = False) -> int:
        """Return ticket limits based on execution mode."""
        if async_mode:
            return 50000
        return 500

    def execute(self, form_data: Dict) -> Dict:
        """
        Execute the tool synchronously (for small jobs or dry-run).
        This is used for ≤500 tickets or when dry_run is enabled.
        """
        view_id = int(form_data.get('view_id'))
        operation = form_data.get('operation')
        tags_input = form_data.get('tags', '').strip()
        ticket_limit = int(form_data.get('ticket_limit'))
        dry_run = form_data.get('dry_run') == 'on'

        # Parse tags (split by comma, strip whitespace)
        tags = [tag.strip() for tag in tags_input.split(',') if tag.strip()]

        try:
            # Fetch tickets from the view
            tickets = get_view_tickets(view_id, limit=ticket_limit)

            if not tickets:
                return {
                    'success': True,
                    'message': 'No tickets found in the selected view.',
                    'data': {
                        'view_id': view_id,
                        'operation': operation,
                        'tags': tags,
                        'total_tickets': 0,
                        'processed': 0,
                        'dry_run': dry_run
                    }
                }

            ticket_ids = [ticket.id for ticket in tickets]

            # Get view details
            views = get_all_views()
            view_name = next((v.title for v in views if v.id == view_id), f"View {view_id}")

            if dry_run:
                # Dry run - just show what would be affected
                ticket_details = [
                    {
                        'id': ticket.id,
                        'subject': ticket.subject,
                        'status': ticket.status,
                        'current_tags': ticket.tags if hasattr(ticket, 'tags') else []
                    }
                    for ticket in tickets
                ]

                return {
                    'success': True,
                    'message': f'DRY RUN: Found {len(tickets)} ticket(s) in view "{view_name}". No changes were made.',
                    'data': {
                        'view_id': view_id,
                        'view_name': view_name,
                        'operation': operation,
                        'tags': tags,
                        'total_tickets': len(tickets),
                        'dry_run': True,
                        'tickets': ticket_details
                    }
                }
            else:
                # Execute the tagging operation
                if operation == 'add':
                    results = add_tags_to_tickets(ticket_ids, tags, delay=1.0)
                elif operation == 'remove':
                    results = remove_tags_from_tickets(ticket_ids, tags, delay=1.0)
                else:
                    raise ValueError(f"Invalid operation: {operation}")

                success_count = len(results['successful'])
                fail_count = len(results['failed'])

                if fail_count == 0:
                    message = f'Successfully {operation}ed tags to {success_count} ticket(s) in view "{view_name}".'
                else:
                    message = f'{operation.capitalize()}ed tags to {success_count} ticket(s). {fail_count} ticket(s) failed.'

                return {
                    'success': True,
                    'message': message,
                    'data': {
                        'view_id': view_id,
                        'view_name': view_name,
                        'operation': operation,
                        'tags': tags,
                        'total_tickets': len(tickets),
                        'successful': success_count,
                        'failed': fail_count,
                        'dry_run': False,
                        'successful_tickets': results['successful'],
                        'failed_tickets': results['failed'],
                        'errors': results['errors']
                    }
                }

        except Exception as e:
            return {
                'success': False,
                'message': f'Error: {str(e)}',
                'data': None
            }

    def execute_async(self, form_data: Dict, job_id: str) -> Dict:
        """
        Execute the tool asynchronously for large datasets (>500 tickets).
        Dispatches a Celery task and returns job information.
        """
        from flask_login import current_user
        from app.models import Job
        from app.tasks.zendesk_tasks import tag_tickets_async

        view_id = int(form_data.get('view_id'))
        operation = form_data.get('operation')
        tags_input = form_data.get('tags', '').strip()
        ticket_limit = int(form_data.get('ticket_limit'))

        # Parse tags
        tags = [tag.strip() for tag in tags_input.split(',') if tag.strip()]

        try:
            # Fetch tickets from the view
            tickets = get_view_tickets(view_id, limit=ticket_limit)

            if not tickets:
                return {
                    'success': False,
                    'message': 'No tickets found in the selected view.',
                    'data': None
                }

            ticket_ids = [ticket.id for ticket in tickets]

            # Create job record in database
            job = Job.create_job(
                job_id=job_id,
                tool_slug=self.slug,
                total_items=len(ticket_ids),
                user_id=current_user.id
            )

            # Dispatch Celery task
            task = tag_tickets_async.apply_async(
                args=[job_id, ticket_ids, tags, operation],
                task_id=job_id
            )

            return {
                'success': True,
                'job_id': job_id,
                'job_db_id': job.id,
                'message': f'Job started. Processing {len(ticket_ids)} tickets in the background...'
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'Error starting async job: {str(e)}',
                'data': None
            }

    def get_export_formats(self) -> list:
        """This tool supports CSV and JSON export."""
        return ['csv', 'json']

    def export_results(self, results: Dict, format: str) -> Tuple[bytes, str, str]:
        """Export results in the specified format."""
        data = results.get('data', {})

        if format == 'csv':
            output = StringIO()
            writer = csv.writer(output)

            # Write header information
            writer.writerow(['Tag Manager Results'])
            writer.writerow(['View', data.get('view_name', 'N/A')])
            writer.writerow(['Operation', data.get('operation', 'N/A')])
            writer.writerow(['Tags', ', '.join(data.get('tags', []))])
            writer.writerow(['Total Tickets', data.get('total_tickets', 0)])
            writer.writerow(['Dry Run', 'Yes' if data.get('dry_run') else 'No'])

            if not data.get('dry_run'):
                writer.writerow(['Successful', data.get('successful', 0)])
                writer.writerow(['Failed', data.get('failed', 0)])

            writer.writerow([])

            # Write ticket details
            if data.get('dry_run'):
                writer.writerow(['Ticket ID', 'Subject', 'Status', 'Current Tags'])
                for ticket in data.get('tickets', []):
                    writer.writerow([
                        ticket.get('id'),
                        ticket.get('subject'),
                        ticket.get('status'),
                        ', '.join(ticket.get('current_tags', []))
                    ])
            else:
                # Write errors if any
                if data.get('errors'):
                    writer.writerow(['Errors'])
                    for error in data.get('errors', []):
                        writer.writerow([error])

            csv_data = output.getvalue()
            filename = f"tag_manager_{data.get('view_id', 'unknown')}.csv"
            return (csv_data.encode('utf-8'), 'text/csv', filename)

        elif format == 'json':
            json_data = json.dumps(data, indent=2)
            filename = f"tag_manager_{data.get('view_id', 'unknown')}.json"
            return (json_data.encode('utf-8'), 'application/json', filename)

        else:
            raise ValueError(f"Unsupported export format: {format}")
