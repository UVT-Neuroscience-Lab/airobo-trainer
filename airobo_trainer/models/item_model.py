"""
Item Model - Manages application data
Follows the Model component of MVC architecture
"""

from typing import List, Optional


class ItemModel:
    """
    Model class for managing a list of items.

    This class handles all data operations including adding, removing,
    and retrieving items from the internal data structure.
    """

    def __init__(self) -> None:
        """Initialize the model with prepopulated items."""
        self._items: List[str] = ["Text Commands", "Avatar", "Video"]

    def remove_item(self, index: int) -> bool:
        """
        Remove an item at the specified index.

        Args:
            index: The index of the item to remove

        Returns:
            True if item was removed successfully, False if index is invalid
        """
        if 0 <= index < len(self._items):
            self._items.pop(index)
            return True
        return False

    def get_item(self, index: int) -> Optional[str]:
        """
        Get an item at the specified index.

        Args:
            index: The index of the item to retrieve

        Returns:
            The item at the specified index, or None if index is invalid
        """
        if 0 <= index < len(self._items):
            return self._items[index]
        return None

    def get_all_items(self) -> List[str]:
        """
        Get all items in the list.

        Returns:
            A copy of the items list
        """
        return self._items.copy()

    def clear_all(self) -> None:
        """Clear all items from the list."""
        self._items.clear()

    def get_count(self) -> int:
        """
        Get the number of items in the list.

        Returns:
            The number of items
        """
        return len(self._items)

