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

    def test_handle_remove_item_success(self, controller):
        """Test successfully removing an item through controller."""
        controller._handle_remove_item(0)
        assert controller.model.get_count() == 2
        assert controller.view.list_widget.count() == 2

    def test_handle_remove_item_invalid_index(self, controller, monkeypatch):
        """Test removing an item with invalid index shows warning."""
        warning_calls = []
        monkeypatch.setattr(
            controller.view, "show_warning",
            lambda *args: warning_calls.append(args)
        )

        controller._handle_remove_item(5)
        assert len(warning_calls) == 1
        assert controller.model.get_count() == 3

    def test_handle_clear_all(self, controller):
        """Test clearing all items through controller."""
        assert controller.model.get_count() == 3

        controller._handle_clear_all()
        assert controller.model.get_count() == 0
        assert controller.view.list_widget.count() == 0

    def test_handle_clear_all_empty_list(self, controller):
        """Test clearing when list is already empty."""
        controller._handle_clear_all()
        initial_status = controller.view.status_label.text()
        controller._handle_clear_all()
        # Status should not change when clearing empty list
        assert controller.view.status_label.text() == initial_status

    def test_status_update_prepopulated_items(self, controller):
        """Test status label with prepopulated items."""
        assert controller.view.status_label.text() == "3 items"

    def test_signal_connections(self, controller, qtbot):
        """Test that view signals are properly connected to controller."""
        # Test remove_item_requested signal
        controller.view.list_widget.setCurrentRow(0)
        controller.view.remove_button.click()
        qtbot.wait(100)
        assert controller.model.get_count() == 2

    def test_integration_remove_items(self, controller):
        """Test integration of removing items."""
        assert controller.model.get_count() == 3
        assert controller.view.list_widget.count() == 3

        # Remove middle item
        controller._handle_remove_item(1)
        assert controller.model.get_count() == 2
        assert controller.view.list_widget.count() == 2
        assert controller.view.list_widget.item(0).text() == "Text Commands"
        assert controller.view.list_widget.item(1).text() == "Video"

    def test_show_method(self, controller):
        """Test the show method displays the view."""
        controller.show()
        assert controller.view.isVisible()
