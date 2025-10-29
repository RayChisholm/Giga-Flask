from app.tools.base_tool import BaseTool
from app.tools.registry import ToolRegistry
from app.zendesk.helpers import search_macros_by_text
from typing import Dict, Tuple, Optional
import csv
import json
from io import StringIO


@ToolRegistry.register
class MacroSearchTool(BaseTool):
    """
    Tool to search for macros containing a substring in any of their actions.

    This is useful for finding all macros that reference specific text,
    such as finding all macros that mention a certain field or value.
    """

    name = "Search Macros"
    slug = "macro-search"
    description = "Find macros that contain a substring in any of their actions"
    category = "Macros"
    requires_admin = False

    def get_form_fields(self) -> list:
        """Define the form fields for this tool"""
        return [
            {
                'name': 'search_term',
                'label': 'Search Term',
                'type': 'text',
                'required': True,
                'placeholder': 'Enter text to search for...',
                'help_text': 'This will search within all macro actions. Case-insensitive.'
            }
        ]

    def validate_input(self, form_data: Dict) -> Tuple[bool, Optional[str]]:
        """Validate the search term"""
        search_term = form_data.get('search_term', '').strip()

        if not search_term:
            return False, "Search term is required"

        if len(search_term) < 2:
            return False, "Search term must be at least 2 characters"

        return True, None

    def execute(self, form_data: Dict) -> Dict:
        """Execute the macro search"""
        search_term = form_data.get('search_term', '').strip()

        try:
            # Search for macros
            results = search_macros_by_text(search_term)

            return {
                'success': True,
                'message': f'Found {len(results)} macro(s) matching "{search_term}"',
                'data': {
                    'search_term': search_term,
                    'count': len(results),
                    'macros': results
                }
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'Search failed: {str(e)}',
                'data': None
            }

    def get_export_formats(self) -> list:
        """This tool supports CSV and JSON export"""
        return ['csv', 'json']

    def export_results(self, results: Dict, format: str) -> Tuple[bytes, str, str]:
        """Export results in the specified format"""
        if not results.get('success') or not results.get('data'):
            raise ValueError("No valid results to export")

        macros = results['data'].get('macros', [])
        search_term = results['data'].get('search_term', 'macros')

        if format == 'csv':
            # Create CSV
            output = StringIO()
            writer = csv.writer(output)

            # Write header
            writer.writerow(['Macro ID', 'Title', 'Active', 'Matching Actions', 'URL'])

            # Write data
            for macro in macros:
                actions_str = '; '.join([
                    f"{action['field']}: {action['value']}"
                    for action in macro['matching_actions']
                ])
                writer.writerow([
                    macro['id'],
                    macro['title'],
                    'Yes' if macro['active'] else 'No',
                    actions_str,
                    macro['url']
                ])

            csv_data = output.getvalue()
            return (
                csv_data.encode('utf-8'),
                'text/csv',
                f'macro_search_{search_term}.csv'
            )

        elif format == 'json':
            # Create JSON
            json_data = json.dumps({
                'search_term': search_term,
                'count': len(macros),
                'macros': macros
            }, indent=2)

            return (
                json_data.encode('utf-8'),
                'application/json',
                f'macro_search_{search_term}.json'
            )

        else:
            raise ValueError(f"Unsupported export format: {format}")
