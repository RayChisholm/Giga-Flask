from typing import Dict, Optional, Type
from app.tools.base_tool import BaseTool


class ToolRegistry:
    """
    Registry for auto-discovering and managing tools.

    Tools register themselves using the @ToolRegistry.register decorator.
    This allows for automatic discovery without manually updating route files.
    """

    _tools: Dict[str, Type[BaseTool]] = {}

    @classmethod
    def register(cls, tool_class: Type[BaseTool]) -> Type[BaseTool]:
        """
        Decorator to register a tool class.

        Usage:
            @ToolRegistry.register
            class MyTool(BaseTool):
                ...

        Args:
            tool_class: The tool class to register

        Returns:
            The same tool class (so it can be used as a decorator)
        """
        if not hasattr(tool_class, 'slug') or not tool_class.slug:
            raise ValueError(f"Tool {tool_class.__name__} must define a 'slug' attribute")

        if tool_class.slug in cls._tools:
            raise ValueError(f"Tool with slug '{tool_class.slug}' is already registered")

        cls._tools[tool_class.slug] = tool_class
        print(f"Registered tool: {tool_class.name} ({tool_class.slug})")
        return tool_class

    @classmethod
    def get_tool(cls, slug: str) -> Optional[BaseTool]:
        """
        Get a tool instance by its slug.

        Args:
            slug: The tool's slug identifier

        Returns:
            An instance of the tool, or None if not found
        """
        tool_class = cls._tools.get(slug)
        if tool_class:
            return tool_class()
        return None

    @classmethod
    def get_all_tools(cls) -> Dict[str, Type[BaseTool]]:
        """
        Get all registered tools.

        Returns:
            Dictionary mapping slugs to tool classes
        """
        return cls._tools.copy()

    @classmethod
    def get_tools_by_category(cls, category: str) -> Dict[str, Type[BaseTool]]:
        """
        Get all tools in a specific category.

        Args:
            category: The category name

        Returns:
            Dictionary mapping slugs to tool classes in that category
        """
        return {
            slug: tool_class
            for slug, tool_class in cls._tools.items()
            if tool_class.category == category
        }

    @classmethod
    def get_categories(cls) -> list:
        """
        Get all unique categories.

        Returns:
            List of category names
        """
        categories = set(tool_class.category for tool_class in cls._tools.values())
        return sorted(categories)

    @classmethod
    def tool_exists(cls, slug: str) -> bool:
        """
        Check if a tool with the given slug exists.

        Args:
            slug: The tool's slug identifier

        Returns:
            True if tool exists, False otherwise
        """
        return slug in cls._tools

    @classmethod
    def clear_registry(cls):
        """Clear all registered tools (mainly for testing)"""
        cls._tools.clear()
