# This file imports all tool implementations to ensure they get registered
# When you add a new tool, import it here

from app.tools.implementations.macro_search import MacroSearchTool
from app.tools.implementations.apply_macro_to_view import ApplyMacroToViewTool
from app.tools.implementations.tag_manager import TagManagerTool

__all__ = ['MacroSearchTool', 'ApplyMacroToViewTool', 'TagManagerTool']
