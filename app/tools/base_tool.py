from abc import ABC, abstractmethod
from typing import Dict, Tuple, Optional


class BaseTool(ABC):
    """
    Abstract base class for all tools.

    All tools must inherit from this class and implement the required methods.
    This ensures a consistent interface and makes it easy to add new tools.
    """

    # Class attributes (metadata) - must be defined by subclasses
    name: str = ""                      # Display name for the tool
    slug: str = ""                      # URL-safe identifier (e.g., "macro-search")
    description: str = ""               # Brief description of what the tool does
    category: str = "General"           # Category for grouping tools
    requires_admin: bool = False        # Whether tool requires admin privileges

    def __init__(self):
        """Initialize the tool"""
        if not self.name or not self.slug:
            raise ValueError(f"Tool {self.__class__.__name__} must define 'name' and 'slug'")

    @abstractmethod
    def get_form_fields(self) -> list:
        """
        Return a list of form field definitions.

        Each field is a dict with:
        - name: str - Field name
        - label: str - Display label
        - type: str - Input type (text, textarea, select, checkbox, number)
        - required: bool - Whether field is required
        - placeholder: str (optional) - Placeholder text
        - help_text: str (optional) - Help text below field
        - options: list (optional) - For select fields

        Example:
        [
            {
                'name': 'search_term',
                'label': 'Search Term',
                'type': 'text',
                'required': True,
                'placeholder': 'Enter text to search for...',
                'help_text': 'This will search in all macro actions'
            }
        ]
        """
        pass

    @abstractmethod
    def validate_input(self, form_data: Dict) -> Tuple[bool, Optional[str]]:
        """
        Validate form input.

        Args:
            form_data: Dictionary of form field values

        Returns:
            Tuple of (is_valid, error_message)
            - is_valid: True if validation passed
            - error_message: Error message if validation failed, None otherwise
        """
        pass

    @abstractmethod
    def execute(self, form_data: Dict) -> Dict:
        """
        Execute the tool with the given form data.

        Args:
            form_data: Dictionary of validated form field values

        Returns:
            Dictionary containing results with at minimum:
            - success: bool - Whether execution was successful
            - message: str - Success or error message
            - data: any - Tool-specific result data

        Example:
        {
            'success': True,
            'message': 'Found 5 macros matching your search',
            'data': {
                'count': 5,
                'items': [...]
            }
        }
        """
        pass

    def get_template(self) -> str:
        """
        Return the template path for this tool.
        Override this to use a custom template.

        Returns:
            Path to template file (relative to templates directory)
        """
        return 'tools/tool_base.html'

    def supports_async(self) -> bool:
        """
        Whether this tool supports asynchronous execution.
        Override this to return True for long-running operations.

        Returns:
            True if tool can run asynchronously
        """
        return False

    def get_ticket_limit(self, async_mode: bool = False) -> int:
        """
        Get the maximum ticket limit for this tool.

        Args:
            async_mode: Whether the tool is running in async mode

        Returns:
            Maximum number of tickets (500 for sync, 50000 for async by default)
        """
        if async_mode:
            return 50000
        return 500

    def execute_async(self, form_data: Dict, job_id: str) -> Dict:
        """
        Execute the tool asynchronously.
        Override this for tools that support async execution.

        This method should dispatch a Celery task and return immediately
        with the job information. The actual work is done by the Celery task.

        Args:
            form_data: Dictionary of validated form field values
            job_id: Celery task ID for tracking

        Returns:
            Dictionary containing:
            - success: bool
            - job_id: str - Celery task ID
            - message: str - Message for user

        Example:
        {
            'success': True,
            'job_id': 'abc-123-def-456',
            'message': 'Job started. Processing 5000 tickets...'
        }
        """
        raise NotImplementedError("Async execution not implemented for this tool")

    def get_export_formats(self) -> list:
        """
        Return list of supported export formats.
        Override this to enable export functionality.

        Returns:
            List of format strings (e.g., ['csv', 'json', 'xlsx'])
        """
        return []

    def export_results(self, results: Dict, format: str) -> Tuple[bytes, str, str]:
        """
        Export results in the specified format.
        Override this if get_export_formats() returns formats.

        Args:
            results: The results dictionary from execute()
            format: The requested export format

        Returns:
            Tuple of (file_content, mimetype, filename)
        """
        raise NotImplementedError("Export not implemented for this tool")

    def __repr__(self):
        return f'<Tool: {self.name} ({self.slug})>'
