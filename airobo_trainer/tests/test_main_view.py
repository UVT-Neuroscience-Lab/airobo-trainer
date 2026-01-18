"""
Unit tests for MainView
"""

import pytest
from pytestqt.qtbot import QtBot

from airobo_trainer.views.main_view import MainView


class TestMainView:
    """Test suite for the MainView class."""

    @pytest.fixture
    def view(self, qtbot: QtBot):
        """Create a MainView instance for testing."""
        view = MainView()
        qtbot.addWidget(view)
        return view

    def test_init(self, view):
        """Test view initialization."""
        assert view.windowTitle() == "AiRobo-Trainer - MVC Boilerplate"
        assert view.list_widget is not None
        assert view.remove_button is not None
        assert view.clear_button is not None
        assert view.status_label is not None

    def test_update_list(self, view):
        """Test updating the list widget."""
        items = ["Item 1", "Item 2", "Item 3"]
        view.update_list(items)
        assert view.list_widget.count() == 3
        assert view.list_widget.item(0).text() == "Item 1"
        assert view.list_widget.item(1).text() == "Item 2"
        assert view.list_widget.item(2).text() == "Item 3"

    def test_update_list_empty(self, view):
        """Test updating the list with empty list."""
        view.update_list(["Item 1"])
        view.update_list([])
        assert view.list_widget.count() == 0

    def test_set_status(self, view):
        """Test setting status message."""
        view.set_status("Test Status")
        assert view.status_label.text() == "Test Status"

    def test_get_selected_index_no_selection(self, view):
        """Test getting selected index when nothing is selected."""
        view.update_list(["Item 1", "Item 2"])
        assert view.get_selected_index() == -1

    def test_get_selected_index_with_selection(self, view):
        """Test getting selected index when item is selected."""
        view.update_list(["Item 1", "Item 2", "Item 3"])
        view.list_widget.setCurrentRow(1)
        assert view.get_selected_index() == 1

    def test_remove_button_clicked_signal(self, view, qtbot):
        """Test that clicking remove button emits signal."""
        view.update_list(["Item 1", "Item 2"])
        view.list_widget.setCurrentRow(0)
        with qtbot.waitSignal(view.remove_item_requested, timeout=1000) as blocker:
            view.remove_button.click()
        assert blocker.args[0] == 0

    def test_clear_button_clicked_signal(self, view, qtbot):
        """Test that clicking clear button emits signal."""
        view.update_list(["Item 1", "Item 2"])
        with qtbot.waitSignal(view.clear_all_requested, timeout=1000):
            view.clear_button.click()

    def test_clear_button_empty_list(self, view, qtbot):
        """Test that clicking clear button with empty list does not emit signal."""
        view.update_list([])
        with qtbot.assertNotEmitted(view.clear_all_requested, wait=100):
            view.clear_button.click()

    def test_show_info_dialog(self, view, qtbot, monkeypatch):
        """Test showing info dialog."""
        # Mock QMessageBox.information to avoid actual dialog
        calls = []
        monkeypatch.setattr(
            "airobo_trainer.views.main_view.QMessageBox.information",
            lambda *args: calls.append(args)
        )
        view.show_info("Test Title", "Test Message")
        assert len(calls) == 1

    def test_show_warning_dialog(self, view, qtbot, monkeypatch):
        """Test showing warning dialog."""
        # Mock QMessageBox.warning to avoid actual dialog
        calls = []
        monkeypatch.setattr(
            "airobo_trainer.views.main_view.QMessageBox.warning",
            lambda *args: calls.append(args)
        )
        view.show_warning("Test Title", "Test Message")
        assert len(calls) == 1

    def test_show_error_dialog(self, view, qtbot, monkeypatch):
        """Test showing error dialog."""
        # Mock QMessageBox.critical to avoid actual dialog
        calls = []
        monkeypatch.setattr(
            "airobo_trainer.views.main_view.QMessageBox.critical",
            lambda *args: calls.append(args)
        )
        view.show_error("Test Title", "Test Message")
        assert len(calls) == 1
