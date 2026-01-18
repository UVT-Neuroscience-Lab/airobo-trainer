"""
Unit tests for MainController
"""

import pytest
from pytestqt.qtbot import QtBot

from airobo_trainer.models.item_model import ItemModel
from airobo_trainer.views.main_view import MainView
from airobo_trainer.controllers.main_controller import MainController


class TestMainController:
    """Test suite for the MainController class."""

    @pytest.fixture
    def model(self):
        """Create a fresh ItemModel instance."""
        return ItemModel()

    @pytest.fixture
    def view(self, qtbot: QtBot):
        """Create a MainView instance."""
        view = MainView()
        qtbot.addWidget(view)
        return view

    @pytest.fixture
    def controller(self, model, view):
        """Create a MainController instance with model and view."""
        return MainController(model=model, view=view)

    def test_init(self, controller):
        """Test controller initialization."""
        assert controller.model is not None
        assert controller.view is not None

    def test_init_without_model_and_view(self, qtbot):
        """Test controller initialization without providing model and view."""
        controller = MainController()
        qtbot.addWidget(controller.view)
        assert isinstance(controller.model, ItemModel)
        assert isinstance(controller.view, MainView)

    def test_get_model(self, controller, model):
        """Test getting the model instance."""
        assert controller.get_model() is model

    def test_get_view(self, controller, view):
        """Test getting the view instance."""
        assert controller.get_view() is view

    def test_status_update_prepopulated_items(self, controller):
        """Test status label with prepopulated items."""
        assert controller.view.status_label.text() == "3 items"

    def test_show_method(self, controller):
        """Test the show method displays the view."""
        controller.show()
        assert controller.view.isVisible()

    def test_get_bci_config_view(self, controller):
        """Test getting the BCI configuration view instance."""
        bci_view = controller.get_bci_config_view()
        assert bci_view is not None
        assert hasattr(bci_view, "back_requested")

    def test_signal_connections(self, controller):
        """Test that view signals are properly connected to controller."""
        # Test configure_bci_requested signal connection
        controller.main_view.configure_bci_requested.emit()
        # Should switch to BCI config view
        assert controller.current_view == controller.bci_config_view

    def test_show_bci_config(self, controller):
        """Test showing BCI configuration view."""
        controller._show_bci_config()
        assert controller.current_view == controller.bci_config_view
        assert not controller.main_view.isVisible()
        # Note: bci_config_view visibility check would require qtbot

    def test_show_main_view(self, controller):
        """Test showing main view from BCI config."""
        # First switch to BCI config
        controller._show_bci_config()
        assert controller.current_view == controller.bci_config_view

        # Then switch back to main
        controller._show_main_view()
        assert controller.current_view == controller.main_view
        # Should refresh the view data
        assert controller.view.list_widget.count() == 3

    def test_navigation_workflow(self, controller):
        """Test complete navigation workflow."""
        # Start on main view
        assert controller.current_view == controller.main_view

        # Navigate to BCI config
        controller._show_bci_config()
        assert controller.current_view == controller.bci_config_view

        # Navigate back to main
        controller._show_main_view()
        assert controller.current_view == controller.main_view
