from typing import List, Optional, Dict
import time
from zenpy.lib.exception import ZenpyException
from app.zendesk.client import ZendeskClientManager


def get_all_views() -> List:
    """
    Fetch all views from Zendesk.

    Returns:
        List of view objects

    Raises:
        ZenpyException: If API call fails
    """
    client = ZendeskClientManager.get_client()
    if not client:
        raise Exception("Zendesk client not configured")

    try:
        return list(client.views())
    except ZenpyException as e:
        raise Exception(f"Failed to fetch views: {str(e)}")


def get_all_macros() -> List:
    """
    Fetch all macros from Zendesk.

    Returns:
        List of macro objects

    Raises:
        ZenpyException: If API call fails
    """
    client = ZendeskClientManager.get_client()
    if not client:
        raise Exception("Zendesk client not configured")

    try:
        return list(client.macros())
    except ZenpyException as e:
        raise Exception(f"Failed to fetch macros: {str(e)}")


def get_view_tickets(view_id: int, limit: Optional[int] = None) -> List:
    """
    Fetch all tickets from a specific view.

    Args:
        view_id: The Zendesk view ID
        limit: Optional limit on number of tickets to fetch

    Returns:
        List of ticket objects

    Raises:
        ZenpyException: If API call fails
    """
    client = ZendeskClientManager.get_client()
    if not client:
        raise Exception("Zendesk client not configured")

    try:
        tickets = client.views.tickets(view_id)
        if limit:
            return list(tickets)[:limit]
        return list(tickets)
    except ZenpyException as e:
        raise Exception(f"Failed to fetch tickets from view: {str(e)}")


def search_macros_by_text(search_term: str) -> List[dict]:
    """
    Search for macros that contain the search term in their actions.

    Args:
        search_term: Text to search for

    Returns:
        List of dicts with macro details and matching actions
    """
    macros = get_all_macros()
    results = []

    search_term_lower = search_term.lower()

    for macro in macros:
        matching_actions = []

        # Search in macro actions
        if hasattr(macro, 'actions') and macro.actions:
            for action in macro.actions:
                # Convert action to string for searching
                action_str = str(action).lower()
                if search_term_lower in action_str:
                    matching_actions.append({
                        'field': action.get('field', 'unknown'),
                        'value': action.get('value', '')
                    })

        # If we found matches, add this macro to results
        if matching_actions:
            results.append({
                'id': macro.id,
                'title': macro.title,
                'active': macro.active,
                'matching_actions': matching_actions,
                'url': f"https://{ZendeskClientManager.get_client().subdomain}.zendesk.com/admin/macros/{macro.id}"
            })

    return results


def apply_macro_to_ticket(ticket_id: int, macro_id: int) -> bool:
    """
    Apply a macro to a specific ticket.

    Args:
        ticket_id: The ticket ID
        macro_id: The macro ID

    Returns:
        True if successful

    Raises:
        Exception: If application fails
    """
    client = ZendeskClientManager.get_client()
    if not client:
        raise Exception("Zendesk client not configured")

    try:
        # Get the macro
        macro = client.macros(id=macro_id)

        # Apply macro to ticket
        ticket = client.tickets(id=ticket_id)
        ticket.macro_ids = [macro_id]
        client.tickets.update(ticket)

        return True
    except ZenpyException as e:
        raise Exception(f"Failed to apply macro: {str(e)}")


def add_tags_to_tickets(ticket_ids: List[int], tags: List[str], delay: float = 1.0, progress_callback=None) -> Dict:
    """
    Add tags to multiple tickets with rate limiting.

    Args:
        ticket_ids: List of ticket IDs
        tags: List of tags to add
        delay: Delay between requests in seconds (default 1.0)
        progress_callback: Optional callback function(processed, total)

    Returns:
        Dict with 'successful', 'failed', and 'errors' keys
    """
    client = ZendeskClientManager.get_client()
    if not client:
        raise Exception("Zendesk client not configured")

    results = {
        'successful': [],
        'failed': [],
        'errors': []
    }

    total = len(ticket_ids)

    for i, ticket_id in enumerate(ticket_ids):
        try:
            # Get current ticket
            ticket = client.tickets(id=ticket_id)

            # Get current tags and add new ones (avoiding duplicates)
            current_tags = set(ticket.tags) if ticket.tags else set()
            new_tags = current_tags.union(set(tags))

            # Update ticket with new tags
            ticket.tags = list(new_tags)
            client.tickets.update(ticket)

            results['successful'].append(ticket_id)

            # Call progress callback if provided
            if progress_callback:
                progress_callback(i + 1, total)

            # Add delay between requests (except for last item)
            if i < len(ticket_ids) - 1:
                time.sleep(delay)

        except Exception as e:
            error_msg = str(e)
            # Check if it's a rate limit error
            if '429' in error_msg or 'rate limit' in error_msg.lower():
                time.sleep(60)  # Wait 1 minute
                try:
                    ticket = client.tickets(id=ticket_id)
                    current_tags = set(ticket.tags) if ticket.tags else set()
                    new_tags = current_tags.union(set(tags))
                    ticket.tags = list(new_tags)
                    client.tickets.update(ticket)
                    results['successful'].append(ticket_id)

                    if progress_callback:
                        progress_callback(i + 1, total)
                except Exception as retry_error:
                    results['failed'].append(ticket_id)
                    results['errors'].append(f"Ticket {ticket_id}: {str(retry_error)}")
            else:
                results['failed'].append(ticket_id)
                results['errors'].append(f"Ticket {ticket_id}: {error_msg}")

    return results


def remove_tags_from_tickets(ticket_ids: List[int], tags: List[str], delay: float = 1.0, progress_callback=None) -> Dict:
    """
    Remove tags from multiple tickets with rate limiting.

    Args:
        ticket_ids: List of ticket IDs
        tags: List of tags to remove
        delay: Delay between requests in seconds (default 1.0)
        progress_callback: Optional callback function(processed, total)

    Returns:
        Dict with 'successful', 'failed', and 'errors' keys
    """
    client = ZendeskClientManager.get_client()
    if not client:
        raise Exception("Zendesk client not configured")

    results = {
        'successful': [],
        'failed': [],
        'errors': []
    }

    total = len(ticket_ids)
    tags_to_remove = set(tags)

    for i, ticket_id in enumerate(ticket_ids):
        try:
            # Get current ticket
            ticket = client.tickets(id=ticket_id)

            # Get current tags and remove specified ones
            current_tags = set(ticket.tags) if ticket.tags else set()
            new_tags = current_tags - tags_to_remove

            # Update ticket with remaining tags
            ticket.tags = list(new_tags)
            client.tickets.update(ticket)

            results['successful'].append(ticket_id)

            # Call progress callback if provided
            if progress_callback:
                progress_callback(i + 1, total)

            # Add delay between requests (except for last item)
            if i < len(ticket_ids) - 1:
                time.sleep(delay)

        except Exception as e:
            error_msg = str(e)
            # Check if it's a rate limit error
            if '429' in error_msg or 'rate limit' in error_msg.lower():
                time.sleep(60)  # Wait 1 minute
                try:
                    ticket = client.tickets(id=ticket_id)
                    current_tags = set(ticket.tags) if ticket.tags else set()
                    new_tags = current_tags - tags_to_remove
                    ticket.tags = list(new_tags)
                    client.tickets.update(ticket)
                    results['successful'].append(ticket_id)

                    if progress_callback:
                        progress_callback(i + 1, total)
                except Exception as retry_error:
                    results['failed'].append(ticket_id)
                    results['errors'].append(f"Ticket {ticket_id}: {str(retry_error)}")
            else:
                results['failed'].append(ticket_id)
                results['errors'].append(f"Ticket {ticket_id}: {error_msg}")

    return results


def apply_macro_to_tickets(ticket_ids: List[int], macro_id: int, delay: float = 1.0, progress_callback=None) -> Dict:
    """
    Apply a macro to multiple tickets with rate limiting.

    Args:
        ticket_ids: List of ticket IDs
        macro_id: The macro ID to apply
        delay: Delay between requests in seconds (default 1.0)
        progress_callback: Optional callback function(processed, total)

    Returns:
        Dict with 'successful', 'failed', and 'errors' keys
    """
    client = ZendeskClientManager.get_client()
    if not client:
        raise Exception("Zendesk client not configured")

    results = {
        'successful': [],
        'failed': [],
        'errors': []
    }

    total = len(ticket_ids)

    for i, ticket_id in enumerate(ticket_ids):
        try:
            # Apply macro
            apply_macro_to_ticket(ticket_id, macro_id)
            results['successful'].append(ticket_id)

            # Call progress callback if provided
            if progress_callback:
                progress_callback(i + 1, total)

            # Add delay between requests to avoid rate limiting (except for last item)
            if i < len(ticket_ids) - 1:
                time.sleep(delay)

        except Exception as e:
            error_msg = str(e)
            # Check if it's a rate limit error (429 status code in message)
            if '429' in error_msg or 'rate limit' in error_msg.lower():
                # If we hit rate limit, wait and retry once
                time.sleep(60)  # Wait 1 minute
                try:
                    apply_macro_to_ticket(ticket_id, macro_id)
                    results['successful'].append(ticket_id)

                    if progress_callback:
                        progress_callback(i + 1, total)
                except Exception as retry_error:
                    results['failed'].append(ticket_id)
                    results['errors'].append(f"Ticket {ticket_id}: {str(retry_error)}")
            else:
                results['failed'].append(ticket_id)
                results['errors'].append(f"Ticket {ticket_id}: {error_msg}")

    return results
