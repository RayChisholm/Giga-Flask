from typing import Dict, Tuple, Optional
import csv
import json
from io import StringIO
from app.tools.base_tool import BaseTool
from app.tools.registry import ToolRegistry
from app.zendesk.helpers import get_all_views, get_all_macros, get_view_tickets, apply_macro_to_tickets


@ToolRegistry.register
class ApplyMacroToViewTool(BaseTool):
    """
    Tool to apply a macro to all tickets in a Zendesk view.
    Includes safety features like ticket limits and dry run mode.
    """

    name = "Apply Macro to View"
    slug = "apply-macro-to-view"
    description = "Apply a macro to all tickets in a specified view with safety controls"
    category = "Macros"
    requires_admin = True  # This is a potentially destructive operation

    def get_form_fields(self) -> list:
        """Define the form fields for this tool."""
        try:
            # Fetch views and macros for dropdowns
            views = get_all_views()
            macros = get_all_macros()

            view_options = [
                {
                    'value': str(view.id),
                    'label': f"{view.title} (ID: {view.id})"
                }
                for view in views
            ]

            # Only show active macros
            macro_options = [
                {
                    'value': str(macro.id),
                    'label': f"{macro.title} (ID: {macro.id})"
                }
                for macro in macros
                if macro.active
            ]

        except Exception as e:
            view_options = [{'value': 'error', 'label': f'Error loading views: {str(e)}'}]
            macro_options = [{'value': 'error', 'label': f'Error loading macros: {str(e)}'}]

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
                'name': 'macro_id',
                'label': 'Select Macro',
                'type': 'select',
                'required': True,
                'options': macro_options,
                'help_text': 'Choose the macro to apply to all tickets in the view'
            },
            {
                'name': 'ticket_limit',
                'label': 'Ticket Limit',
                'type': 'number',
                'required': True,
                'placeholder': '50',
                'help_text': 'Maximum number of tickets to process (recommended: start with 10-50 for testing). Maximum allowed: 500.'
            },
            {
                'name': 'dry_run',
                'label': 'Dry Run (Preview Only)',
                'type': 'checkbox',
                'required': False,
                'help_text': 'Check this box to preview which tickets would be affected without actually applying the macro'
            }
        ]

    def validate_input(self, form_data: Dict) -> Tuple[bool, Optional[str]]:
        """Validate the form input."""
        view_id = form_data.get('view_id')
        macro_id = form_data.get('macro_id')
        ticket_limit = form_data.get('ticket_limit')

        if not view_id:
            return False, "Please select a view"

        if view_id == 'error':
            return False, "Unable to load views. Please check your Zendesk configuration."

        if not macro_id:
            return False, "Please select a macro"

        if macro_id == 'error':
            return False, "Unable to load macros. Please check your Zendesk configuration."

        if not ticket_limit:
            return False, "Please specify a ticket limit"

        try:
            limit = int(ticket_limit)
            if limit < 1:
                return False, "Ticket limit must be at least 1"
            if limit > 500:
                return False, "Ticket limit cannot exceed 500 for safety. Please process in smaller batches."
        except ValueError:
            return False, "Ticket limit must be a valid number"

        return True, None

    def execute(self, form_data: Dict) -> Dict:
        """Execute the tool."""
        view_id = int(form_data.get('view_id'))
        macro_id = int(form_data.get('macro_id'))
        ticket_limit = int(form_data.get('ticket_limit'))
        dry_run = form_data.get('dry_run') == 'on'

        try:
            # Fetch tickets from the view
            tickets = get_view_tickets(view_id, limit=ticket_limit)

            if not tickets:
                return {
                    'success': True,
                    'message': 'No tickets found in the selected view.',
                    'data': {
                        'view_id': view_id,
                        'macro_id': macro_id,
                        'total_tickets': 0,
                        'processed': 0,
                        'dry_run': dry_run
                    }
                }

            ticket_ids = [ticket.id for ticket in tickets]

            # Get view and macro details for the response
            views = get_all_views()
            macros = get_all_macros()

            view_name = next((v.title for v in views if v.id == view_id), f"View {view_id}")
            macro_name = next((m.title for m in macros if m.id == macro_id), f"Macro {macro_id}")

            if dry_run:
                # Dry run - just show what would be affected
                ticket_details = [
                    {
                        'id': ticket.id,
                        'subject': ticket.subject,
                        'status': ticket.status,
                        'priority': getattr(ticket, 'priority', 'N/A')
                    }
                    for ticket in tickets
                ]

                return {
                    'success': True,
                    'message': f'DRY RUN: Found {len(tickets)} ticket(s) in view "{view_name}". No changes were made.',
                    'data': {
                        'view_id': view_id,
                        'view_name': view_name,
                        'macro_id': macro_id,
                        'macro_name': macro_name,
                        'total_tickets': len(tickets),
                        'dry_run': True,
                        'tickets': ticket_details
                    }
                }
            else:
                # Actually apply the macro
                results = apply_macro_to_tickets(ticket_ids, macro_id, delay=1.0)

                # Get details for successful and failed tickets
                successful_tickets = [
                    {
                        'id': ticket.id,
                        'subject': ticket.subject,
                        'status': 'Updated'
                    }
                    for ticket in tickets if ticket.id in results['successful']
                ]

                failed_tickets = [
                    {
                        'id': ticket_id,
                        'error': next((e for e in results['errors'] if str(ticket_id) in e), 'Unknown error')
                    }
                    for ticket_id in results['failed']
                ]

                success_count = len(results['successful'])
                fail_count = len(results['failed'])

                if fail_count == 0:
                    message = f'Successfully applied macro "{macro_name}" to {success_count} ticket(s) in view "{view_name}".'
                else:
                    message = f'Applied macro to {success_count} ticket(s). {fail_count} ticket(s) failed.'

                return {
                    'success': True,
                    'message': message,
                    'data': {
                        'view_id': view_id,
                        'view_name': view_name,
                        'macro_id': macro_id,
                        'macro_name': macro_name,
                        'total_tickets': len(tickets),
                        'successful': success_count,
                        'failed': fail_count,
                        'dry_run': False,
                        'successful_tickets': successful_tickets,
                        'failed_tickets': failed_tickets,
                        'errors': results['errors']
                    }
                }

        except Exception as e:
            return {
                'success': False,
                'message': f'Error: {str(e)}',
                'data': None
            }

    def get_export_formats(self) -> list:
        """Define available export formats."""
        return ['csv', 'json']

    def export_results(self, results: Dict, format: str) -> Tuple[bytes, str, str]:
        """Export results in the specified format."""
        data = results.get('data', {})

        if format == 'csv':
            output = StringIO()
            writer = csv.writer(output)

            # Write header information
            writer.writerow(['Apply Macro to View Results'])
            writer.writerow(['View', data.get('view_name', 'N/A')])
            writer.writerow(['Macro', data.get('macro_name', 'N/A')])
            writer.writerow(['Total Tickets', data.get('total_tickets', 0)])
            writer.writerow(['Dry Run', 'Yes' if data.get('dry_run') else 'No'])

            if not data.get('dry_run'):
                writer.writerow(['Successful', data.get('successful', 0)])
                writer.writerow(['Failed', data.get('failed', 0)])

            writer.writerow([])

            # Write ticket details
            if data.get('dry_run'):
                writer.writerow(['Ticket ID', 'Subject', 'Status', 'Priority'])
                for ticket in data.get('tickets', []):
                    writer.writerow([
                        ticket.get('id'),
                        ticket.get('subject'),
                        ticket.get('status'),
                        ticket.get('priority')
                    ])
            else:
                # Write successful tickets
                if data.get('successful_tickets'):
                    writer.writerow(['Successful Tickets'])
                    writer.writerow(['Ticket ID', 'Subject', 'Status'])
                    for ticket in data.get('successful_tickets', []):
                        writer.writerow([
                            ticket.get('id'),
                            ticket.get('subject'),
                            ticket.get('status')
                        ])
                    writer.writerow([])

                # Write failed tickets
                if data.get('failed_tickets'):
                    writer.writerow(['Failed Tickets'])
                    writer.writerow(['Ticket ID', 'Error'])
                    for ticket in data.get('failed_tickets', []):
                        writer.writerow([
                            ticket.get('id'),
                            ticket.get('error')
                        ])

            csv_data = output.getvalue()
            filename = f"apply_macro_{data.get('view_id', 'unknown')}.csv"
            return (csv_data.encode('utf-8'), 'text/csv', filename)

        elif format == 'json':
            json_data = json.dumps(data, indent=2)
            filename = f"apply_macro_{data.get('view_id', 'unknown')}.json"
            return (json_data.encode('utf-8'), 'application/json', filename)

        else:
            raise ValueError(f"Unsupported export format: {format}")

    def get_template(self) -> str:
        """Use custom template for this tool."""
        return 'tools/apply_macro_to_view.html'
