from flask import render_template
from flask_login import login_required
from app.main import main_bp
from app.tools.registry import ToolRegistry


@main_bp.route('/')
@login_required
def index():
    """Landing page / Dashboard"""
    # Get all registered tools grouped by category
    all_tools = ToolRegistry.get_all_tools()
    tools_by_category = {}

    for slug, tool_class in all_tools.items():
        category = tool_class.category
        if category not in tools_by_category:
            tools_by_category[category] = []
        tools_by_category[category].append({
            'name': tool_class.name,
            'slug': tool_class.slug,
            'description': tool_class.description,
            'requires_admin': tool_class.requires_admin
        })

    return render_template('main/index.html',
                         title='Dashboard',
                         tools_by_category=tools_by_category)
