"""
Main Controller - Application Logic and Signal Handling
Follows the Controller component of MVC architecture
"""

from typing import Optional

from airobo_trainer.models.item_model import ItemModel
from airobo_trainer.views.main_view import MainView
from airobo_trainer.views.bci_config_view import BCIConfigView
from airobo_trainer.views.experiment_config_view import ExperimentConfigView
from airobo_trainer.views.experiment_views import (
    TextCommandsExperimentView,
    AvatarExperimentView,
    VideoExperimentView,
)


class MainController:
    """
    Main application controller.

    This class coordinates between the Model and View, handling all
    business logic and connecting UI signals to model operations.
    """

    def __init__(self, model: Optional[ItemModel] = None, view: Optional[MainView] = None) -> None:
        """
        Initialize the controller with model and views.

        Args:
            model: The data model (creates new if None)
            view: The main view component (creates new if None)
        """
        self.model = model if model is not None else ItemModel()
        self.main_view = view if view is not None else MainView()
        self.bci_config_view = BCIConfigView()
        self.experiment_config_view = ExperimentConfigView()
        self.current_experiment_view = None  # Track current experiment view
        self.current_view = self.main_view  # Track which view is currently active

        # Connect view signals to controller methods
        self._connect_signals()

        # Initialize the view with current model data
        self._update_view()

    def _connect_signals(self) -> None:
        """Connect view signals to controller handler methods."""
        self.main_view.configure_bci_requested.connect(self._show_bci_config)
        self.main_view.configure_experiment_requested.connect(self._show_experiment_config)
        self.main_view.experiment_selected.connect(self._show_experiment)
        self.bci_config_view.back_requested.connect(self._show_main_view)
        self.experiment_config_view.back_requested.connect(self._show_main_view)

    def _update_view(self) -> None:
        """Update the main view with current model data."""
        items = self.model.get_all_items()
        self.main_view.update_list(items)
        self._update_status()

    def _update_status(self) -> None:
        """Update the status label with current item count."""
        # Only update status for views that have status functionality
        if hasattr(self.current_view, "set_status"):
            count = self.model.get_count()
            if count == 0:
                self.current_view.set_status("No items")
            elif count == 1:
                self.current_view.set_status("1 item")
            else:
                self.current_view.set_status(f"{count} items")

    def _show_bci_config(self) -> None:
        """Show the BCI configuration view."""
        self.main_view.hide()
        self.bci_config_view.show()
        self.current_view = self.bci_config_view

    def _show_experiment_config(self) -> None:
        """Show the experiment configuration view."""
        self.main_view.hide()
        self.experiment_config_view.show()
        self.current_view = self.experiment_config_view

    def _show_main_view(self) -> None:
        """Show the main view."""
        # Hide any current views
        self.bci_config_view.hide()
        self.experiment_config_view.hide()
        if self.current_experiment_view:
            self.current_experiment_view.hide()

        self.main_view.show()
        self.current_view = self.main_view
        self.current_experiment_view = None
        self._update_view()  # Refresh the main view data

    def _show_experiment(self, experiment_name: str) -> None:
        """Show the experiment view for the selected experiment."""
        # Get BCI configuration
        bci_config = self.bci_config_view.get_bci_parameters()
        bci_config["selected_electrodes"] = self.bci_config_view.get_selected_electrodes()

        # Create the appropriate experiment view
        if experiment_name == "Text Commands":
            self.current_experiment_view = TextCommandsExperimentView(experiment_name, bci_config, self.experiment_config_view)
        elif experiment_name == "Avatar":
            self.current_experiment_view = AvatarExperimentView(experiment_name, bci_config, self.experiment_config_view)
        elif experiment_name == "Video":
            self.current_experiment_view = VideoExperimentView(experiment_name, bci_config, self.experiment_config_view)
        else:
            return  # Unknown experiment

        # Connect back signal
        self.current_experiment_view.back_requested.connect(self._show_main_view)

        # Hide main view and show experiment view
        self.main_view.hide()
        self.current_experiment_view.show()
        self.current_view = self.current_experiment_view

    def show(self) -> None:
        """Show the current view window."""
        self.current_view.show()

    def get_model(self) -> ItemModel:
        """
        Get the model instance.

        Returns:
            The model instance
        """
        return self.model

    @property
    def view(self) -> MainView:
        """
        Get the main view instance (backward compatibility property).

        Returns:
            The main view instance
        """
        return self.main_view

    def get_view(self) -> MainView:
        """
        Get the main view instance.

        Returns:
            The main view instance
        """
        return self.main_view

    def get_bci_config_view(self) -> BCIConfigView:
        """
        Get the BCI configuration view instance.

        Returns:
            The BCI configuration view instance
        """
        return self.bci_config_view
