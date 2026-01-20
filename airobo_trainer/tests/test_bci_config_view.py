"""
Unit tests for BCIConfigView
"""

import pytest
from pytestqt.qtbot import QtBot
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import Qt, QPoint

from airobo_trainer.views.bci_config_view import BCIConfigView, ElectrodeWidget


class TestElectrodeWidget:
    """Test suite for the ElectrodeWidget class."""

    @pytest.fixture
    def electrode_widget(self, qtbot: QtBot):
        """Create an ElectrodeWidget instance for testing."""
        widget = ElectrodeWidget()
        qtbot.addWidget(widget)
        return widget

    def test_init(self, electrode_widget):
        """Test electrode widget initialization."""
        assert electrode_widget.selected_electrodes == set()
        assert len(electrode_widget.relative_electrode_positions) == 32

    def test_get_selected_electrodes(self, electrode_widget):
        """Test getting selected electrodes."""
        # Initially empty
        assert electrode_widget.selected_electrodes == set()

        # Select some electrodes
        electrode_widget.selected_electrodes.add(0)
        electrode_widget.selected_electrodes.add(1)

        # Get copy
        selected = electrode_widget.selected_electrodes.copy()
        assert selected == {0, 1}

        # Modify copy, original should not change
        selected.add(2)
        assert electrode_widget.selected_electrodes == {0, 1}

    def test_electrode_positioning(self, electrode_widget):
        """Test that electrode positions are calculated correctly."""
        # Test that absolute positions are calculated from relative positions
        positions = electrode_widget._get_absolute_electrode_positions()
        assert len(positions) == 32  # Should have 32 electrodes

        # All positions should be tuples of (x, y)
        for pos in positions:
            assert isinstance(pos, tuple)
            assert len(pos) == 2
            assert isinstance(pos[0], int)  # x coordinate
            assert isinstance(pos[1], int)  # y coordinate


class TestBCIConfigView:
    """Test suite for the BCIConfigView class."""

    @pytest.fixture
    def bci_view(self, qtbot: QtBot):
        """Create a BCIConfigView instance for testing."""
        view = BCIConfigView()
        qtbot.addWidget(view)
        return view

    def test_init(self, bci_view):
        """Test BCI config view initialization."""
        assert bci_view.windowTitle() == "BCI Configuration"
        assert bci_view.sampling_rate_combo is not None
        assert bci_view.bandpass_combo is not None
        assert bci_view.notch_combo is not None
        assert bci_view.electrode_widget is not None
        assert bci_view.status_label.text() == "Selected 3 electrodes"

    def test_sampling_rate_combo_values(self, bci_view):
        """Test sampling rate combo box has correct values."""
        items = [
            bci_view.sampling_rate_combo.itemText(i)
            for i in range(bci_view.sampling_rate_combo.count())
        ]
        assert items == ["250 Hz", "500 Hz"]

    def test_bandpass_combo_values(self, bci_view):
        """Test bandpass filter combo box has correct values."""
        items = [
            bci_view.bandpass_combo.itemText(i) for i in range(bci_view.bandpass_combo.count())
        ]
        expected = [
            "0.1 – 30 Hz Bandpass",
            "0.1 – 60 Hz Bandpass",
            "0.1 – 100 Hz Bandpass",
            "0.1 – 200 Hz Bandpass",
            "0.5 – 30 Hz Bandpass",
            "0.5 – 60 Hz Bandpass",
            "0.5 – 100 Hz Bandpass",
            "0.5 – 200 Hz Bandpass",
            "2.0 – 30 Hz Bandpass",
            "2.0 – 60 Hz Bandpass",
            "2.0 – 100 Hz Bandpass",
            "2.0 – 200 Hz Bandpass",
            "5.0 – 30 Hz Bandpass",
            "5.0 – 60 Hz Bandpass",
            "5.0 – 100 Hz Bandpass",
            "5.0 – 200 Hz Bandpass",
            "0.1 Hz Highpass",
            "1.0 Hz Highpass",
            "2.0 Hz Highpass",
            "5.0 Hz Highpass",
            "30 Hz Lowpass",
            "60 Hz Lowpass",
            "100 Hz Lowpass",
            "200 Hz Lowpass",
            "None - No filter applied",
        ]
        assert items == expected

    def test_notch_combo_values(self, bci_view):
        """Test notch filter combo box has correct values."""
        items = [bci_view.notch_combo.itemText(i) for i in range(bci_view.notch_combo.count())]
        expected = ["None", "50Hz", "60Hz"]
        assert items == expected

    def test_back_button_signal(self, bci_view, qtbot):
        """Test back button emits signal."""
        with qtbot.waitSignal(bci_view.back_requested, timeout=1000):
            # Find the back button and click it
            for child in bci_view.findChildren(QPushButton):
                if child.text() == "← Back":
                    child.click()
                    break

    def test_get_selected_electrodes(self, bci_view):
        """Test getting selected electrodes from view."""
        # Initially has default electrodes selected
        selected = bci_view.get_selected_electrodes()
        assert selected == {14, 15, 16}

        # Clear and select some electrodes directly on the widget
        bci_view.electrode_widget.selected_electrodes.clear()
        bci_view.electrode_widget.selected_electrodes.add(0)
        bci_view.electrode_widget.selected_electrodes.add(1)

        # Get through view method
        selected = bci_view.get_selected_electrodes()
        assert selected == {0, 1}

    def test_get_bci_parameters(self, bci_view):
        """Test getting BCI parameters."""
        params = bci_view.get_bci_parameters()

        assert isinstance(params, dict)
        assert "sampling_rate" in params
        assert "bandpass_filter" in params
        assert "notch_filter" in params

        assert params["sampling_rate"] == "500 Hz"  # Default is 500 Hz
        assert params["bandpass_filter"] == "0.1 – 60 Hz Bandpass"  # Default at 500 Hz
        assert params["notch_filter"] == "50Hz"  # Default is 50Hz

    def test_electrode_selection_signal(self, bci_view, qtbot):
        """Test electrode selection updates status."""
        # Initially should show "Selected 3 electrodes"
        assert "Selected 3 electrodes" in bci_view.status_label.text()

        # Simulate electrode selection by calling the handler directly
        bci_view._on_electrode_selected(0)  # Select electrode 0
        assert bci_view.status_label.text() == "Selected 3 electrodes"

        # Select another electrode
        bci_view.electrode_widget.selected_electrodes.add(1)
        bci_view._on_electrode_selected(1)
        assert bci_view.status_label.text() == "Selected 4 electrodes"

    def test_parameter_modification(self, bci_view):
        """Test modifying BCI parameters."""
        # Sampling rate is already at 500 Hz, change to 250 Hz
        bci_view.sampling_rate_combo.setCurrentIndex(0)  # 250 Hz
        params = bci_view.get_bci_parameters()
        assert params["sampling_rate"] == "250 Hz"

        # Change bandpass filter to index 1
        bci_view.bandpass_combo.setCurrentIndex(1)  # 0.1 – 60 Hz Bandpass
        params = bci_view.get_bci_parameters()
        assert params["bandpass_filter"] == "0.1 – 60 Hz Bandpass"

        # Change notch filter
        bci_view.notch_combo.setCurrentIndex(1)  # 50Hz
        params = bci_view.get_bci_parameters()
        assert params["notch_filter"] == "50Hz"

    def test_set_status(self, bci_view):
        """Test setting status message."""
        bci_view.set_status("Test message")
        assert bci_view.status_label.text() == "Test message"

    def test_output_path(self, bci_view):
        """Test output path configuration."""
        assert bci_view.output_path_edit.text() == "airobo_trainer/output"

        # Test changing output path
        bci_view.output_path_edit.setText("new/path")
        params = bci_view.get_bci_parameters()
        assert params["output_path"] == "new/path"

    def test_electrode_clicking(self, bci_view, qtbot):
        """Test clicking on electrodes."""
        # Get electrode positions
        positions = bci_view.electrode_widget._get_absolute_electrode_positions()

        # Click on electrode 14 (C3, should be selected by default)
        x, y = positions[14]  # C3 electrode
        qtbot.mouseClick(bci_view.electrode_widget, Qt.MouseButton.LeftButton, pos=QPoint(x, y))

        # Should now be deselected (since it was selected)
        assert 14 not in bci_view.electrode_widget.selected_electrodes

        # Click again to select it
        qtbot.mouseClick(bci_view.electrode_widget, Qt.MouseButton.LeftButton, pos=QPoint(x, y))
        assert 14 in bci_view.electrode_widget.selected_electrodes
