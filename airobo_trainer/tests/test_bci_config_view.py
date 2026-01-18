"""
Unit tests for BCIConfigView
"""

import pytest
from pytestqt.qtbot import QtBot
from PyQt6.QtWidgets import QPushButton

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
        assert bci_view.status_label.text() == "BCI Configuration Ready"

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
            bci_view.bandpass_combo.itemText(i)
            for i in range(bci_view.bandpass_combo.count())
        ]
        expected = ["0.5Hz-50Hz", "1Hz-40Hz", "2Hz-30Hz", "4Hz-20Hz", "8Hz-12Hz", "0.1Hz-100Hz", "None"]
        assert items == expected

    def test_notch_combo_values(self, bci_view):
        """Test notch filter combo box has correct values."""
        items = [
            bci_view.notch_combo.itemText(i)
            for i in range(bci_view.notch_combo.count())
        ]
        expected = ["None", "50Hz", "60Hz", "50Hz + 60Hz", "50Hz (Cascading)", "60Hz (Cascading)"]
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
        # Initially empty
        selected = bci_view.get_selected_electrodes()
        assert selected == set()

        # Select some electrodes directly on the widget
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

        assert params["sampling_rate"] == "250 Hz"  # Default first item
        assert params["bandpass_filter"] == "0.5Hz-50Hz"  # Default first item
        assert params["notch_filter"] == "None"  # Default first item

    def test_electrode_selection_signal(self, bci_view, qtbot):
        """Test electrode selection updates status."""
        # Initially should show "BCI Configuration Ready"
        assert "BCI Configuration Ready" in bci_view.status_label.text()

        # Simulate electrode selection by calling the handler directly
        bci_view._on_electrode_selected(0)  # Select electrode 0
        assert bci_view.status_label.text() == "Selected 0 electrodes"

        # Select another electrode
        bci_view.electrode_widget.selected_electrodes.add(1)
        bci_view._on_electrode_selected(1)
        assert bci_view.status_label.text() == "Selected 1 electrodes"

    def test_parameter_modification(self, bci_view):
        """Test modifying BCI parameters."""
        # Change sampling rate
        bci_view.sampling_rate_combo.setCurrentIndex(1)  # 500 Hz
        params = bci_view.get_bci_parameters()
        assert params["sampling_rate"] == "500 Hz"

        # Change bandpass filter
        bci_view.bandpass_combo.setCurrentIndex(1)  # 1Hz-40Hz
        params = bci_view.get_bci_parameters()
        assert params["bandpass_filter"] == "1Hz-40Hz"

        # Change notch filter
        bci_view.notch_combo.setCurrentIndex(1)  # 50Hz
        params = bci_view.get_bci_parameters()
        assert params["notch_filter"] == "50Hz"
