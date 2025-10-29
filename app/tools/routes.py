from flask import render_template, request, flash, redirect, url_for, session, make_response
from flask_login import login_required, current_user
from app.tools import tools_bp
from app.tools.registry import ToolRegistry
import uuid


@tools_bp.route('/<slug>', methods=['GET', 'POST'])
@login_required
def execute_tool(slug):
    """
    Generic route that works for all registered tools.

    This single route handles:
    - Displaying the tool form (GET)
    - Validating input
    - Executing the tool (POST)
    - Displaying results
    """
    # Get the tool from registry
    tool = ToolRegistry.get_tool(slug)

    if not tool:
        flash(f'Tool "{slug}" not found', 'danger')
        return redirect(url_for('main.index'))

    # Check if tool requires admin privileges
    if tool.requires_admin and (not current_user.is_authenticated or not current_user.is_admin()):
        flash('This tool requires administrator privileges.', 'danger')
        return redirect(url_for('main.index'))

    results = None

    # Handle form submission
    if request.method == 'POST':
        # Get form data
        form_data = request.form.to_dict()

        # Validate input
        is_valid, error_message = tool.validate_input(form_data)

        if not is_valid:
            flash(f'Validation error: {error_message}', 'danger')
        else:
            # Check if tool supports async and if ticket count warrants async execution
            dry_run = form_data.get('dry_run') == 'on'
            ticket_limit = int(form_data.get('ticket_limit', 0)) if 'ticket_limit' in form_data else 0
            use_async = (tool.supports_async() and
                        ticket_limit > 500 and
                        not dry_run)

            # Execute the tool
            try:
                if use_async:
                    # Generate unique job ID
                    job_id = str(uuid.uuid4())

                    # Execute async
                    results = tool.execute_async(form_data, job_id)

                    if results.get('success'):
                        flash(results.get('message', 'Job started!'), 'success')
                        # Redirect to job status page
                        return redirect(url_for('jobs.view_job', job_id=results.get('job_db_id')))
                    else:
                        flash(results.get('message', 'Failed to start async job'), 'danger')
                else:
                    # Execute synchronously
                    results = tool.execute(form_data)

                    # Store results in session for export
                    session[f'tool_results_{slug}'] = results

                    # Show success or error message
                    if results.get('success'):
                        flash(results.get('message', 'Tool executed successfully!'), 'success')
                    else:
                        flash(results.get('message', 'Tool execution failed'), 'danger')

            except Exception as e:
                flash(f'Error executing tool: {str(e)}', 'danger')
                results = {
                    'success': False,
                    'message': str(e),
                    'data': None
                }

    # Render the tool page
    return render_template(
        tool.get_template(),
        tool=tool,
        form_fields=tool.get_form_fields(),
        results=results,
        title=tool.name
    )


@tools_bp.route('/<slug>/export/<format>')
@login_required
def export_tool_results(slug, format):
    """
    Export tool results in specified format.

    This route retrieves results from session and exports them.
    """
    tool = ToolRegistry.get_tool(slug)

    if not tool:
        flash(f'Tool "{slug}" not found', 'danger')
        return redirect(url_for('main.index'))

    # Check if tool requires admin privileges
    if tool.requires_admin and (not current_user.is_authenticated or not current_user.is_admin()):
        flash('This tool requires administrator privileges.', 'danger')
        return redirect(url_for('main.index'))

    # Check if export format is supported
    if format not in tool.get_export_formats():
        flash(f'Export format "{format}" not supported for this tool', 'danger')
        return redirect(url_for('tools.execute_tool', slug=slug))

    # Retrieve results from session
    results = session.get(f'tool_results_{slug}')

    if not results:
        flash('No results available to export. Please run the tool first.', 'warning')
        return redirect(url_for('tools.execute_tool', slug=slug))

    # Export the results
    try:
        file_content, mimetype, filename = tool.export_results(results, format)

        # Create response with file download
        response = make_response(file_content)
        response.headers['Content-Type'] = mimetype
        response.headers['Content-Disposition'] = f'attachment; filename={filename}'

        return response

    except Exception as e:
        flash(f'Export failed: {str(e)}', 'danger')
        return redirect(url_for('tools.execute_tool', slug=slug))
