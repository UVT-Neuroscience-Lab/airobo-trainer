"""
Main Controller - Application Logic and Signal Handling
Follows the Controller component of MVC architecture
"""

from typing import Optional

from airobo_trainer.models.item_model import ItemModel
from airobo_trainer.views.main_view import MainView


class MainController:
    """
    Main application controller.

    This class coordinates between the Model and View, handling all
    business logic and connecting UI signals to model operations.
    """

    def __init__(self, model: Optional[ItemModel] = None, view: Optional[MainView] = None) -> None:
        """
        Initialize the controller with model and view.

        Args:
            model: The data model (creates new if None)
            view: The view component (creates new if None)
        """
        self.model = model if model is not None else ItemModel()
        self.view = view if view is not None else MainView()

        # Connect view signals to controller methods
        self._connect_signals()

        # Initialize the view with current model data
        self._update_view()

    def _connect_signals(self) -> None:
        """Connect view signals to controller handler methods."""
        self.view.remove_item_requested.connect(self._handle_remove_item)
        self.view.clear_all_requested.connect(self._handle_clear_all)

    def _update_view(self) -> None:
        """Update the view with current model data."""
        items = self.model.get_all_items()
        self.view.update_list(items)
        self._update_status()

    def _update_status(self) -> None:
        """Update the status label with current item count."""
        count = self.model.get_count()
        if count == 0:
            self.view.set_status("No items")
        elif count == 1:
            self.view.set_status("1 item")
        else:
            self.view.set_status(f"{count} items")

    def _handle_remove_item(self, index: int) -> None:
        """
        Handle the remove item request from the view.

        Args:
            index: The index of the item to remove
        """
        item = self.model.get_item(index)
        if item is None:
            self.view.show_warning("Invalid Selection", "Please select a valid item.")
            return

        success = self.model.remove_item(index)
        if success:
            self._update_view()
            self.view.set_status(f"Removed: {item}")
        else:
            self.view.show_error("Error", "Failed to remove item.")

    def _handle_clear_all(self) -> None:
        """Handle the clear all request from the view."""
        count = self.model.get_count()
        if count == 0:
            return

        self.model.clear_all()
        self._update_view()
        self.view.set_status(f"Cleared {count} item{'s' if count != 1 else ''}")

    def show(self) -> None:
        """Show the main view window."""
        self.view.show()

    def get_model(self) -> ItemModel:
        """
        Get the model instance.

        Returns:
            The model instance
        """
        return self.model

    def get_view(self) -> MainView:
        """
        Get the view instance.

        Returns:
            The view instance
        """
        return self.view
