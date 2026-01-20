"""
Unit tests for Experiment Views
"""

import pytest
from pytestqt.qtbot import QtBot
from unittest.mock import Mock, mock_open, patch
import numpy as np
from PyQt6.QtWidgets import QPushButton, QLabel
from PyQt6.QtCore import Qt

from airobo_trainer.views.experiment_views import (
    BCIWorker,
    MuscleBar,
    BaseExperimentView,
    TextCommandsExperimentView,
    AvatarExperimentView,
    VideoExperimentView,
)


class TestMuscleBar:
    """Test suite for the MuscleBar widget."""

    @pytest.fixture
    def muscle_bar(self, qtbot: QtBot):
        """Create a MuscleBar instance for testing."""
        bar = MuscleBar("Test Arm")
        qtbot.addWidget(bar)
        return bar

    def test_init(self, muscle_bar):
        """Test muscle bar initialization."""
        assert muscle_bar.arm_name == "Test Arm"
        assert len(muscle_bar.activation_levels) == 6
        assert all(level == 0 for level in muscle_bar.activation_levels)

    def test_set_activation_valid(self, muscle_bar):
        """Test setting activation level with valid inputs."""
        muscle_bar.set_activation(0, 50)
        assert muscle_bar.activation_levels[0] == 50

        muscle_bar.set_activation(5, 100)
        assert muscle_bar.activation_levels[5] == 100

    def test_set_activation_invalid_segment(self, muscle_bar):
        """Test setting activation level with invalid segment."""
        # Should not crash or change anything
        muscle_bar.set_activation(10, 50)  # Invalid segment
        assert all(level == 0 for level in muscle_bar.activation_levels)

    def test_set_activation_clamping(self, muscle_bar):
        """Test that activation levels are clamped to 0-100."""
        muscle_bar.set_activation(0, 150)  # Too high
        assert muscle_bar.activation_levels[0] == 100

        muscle_bar.set_activation(1, -10)  # Too low
        assert muscle_bar.activation_levels[1] == 0


class TestBaseExperimentView:
    """Test suite for the BaseExperimentView class."""

    @pytest.fixture
    def base_view(self, qtbot: QtBot):
        """Create a BaseExperimentView instance for testing."""

        # Create a minimal implementation for testing
        class TestExperimentView(BaseExperimentView):
            def _create_center_content(self):
                from PyQt6.QtWidgets import QLabel

                return QLabel("Test Content")

        view = TestExperimentView("Test Experiment")
        qtbot.addWidget(view)
        return view

    def test_init(self, base_view):
        """Test base experiment view initialization."""
        assert base_view.experiment_name == "Test Experiment"
        assert base_view.windowTitle() == "AiRobo-Trainer - Test Experiment"
        assert base_view.left_arm_bar is not None
        assert base_view.right_arm_bar is not None
        assert base_view.current_mode == "relax"

    def test_back_button_signal(self, base_view, qtbot):
        """Test back button emits signal."""
        with qtbot.waitSignal(base_view.back_requested, timeout=1000):
            # Find and click the back button
            back_buttons = base_view.findChildren(QPushButton)
            for button in back_buttons:
                if button.text() == "← Back":
                    button.click()
                    break

    def test_update_muscle_activation(self, base_view):
        """Test updating muscle activation levels."""
        # Test left arm
        base_view.update_muscle_activation("left", 0, 75)
        assert base_view.left_arm_bar.activation_levels[0] == 75

        # Test right arm
        base_view.update_muscle_activation("right", 2, 60)
        assert base_view.right_arm_bar.activation_levels[2] == 60

        # Test invalid arm (should not crash)
        base_view.update_muscle_activation("invalid", 0, 50)

    def test_set_simulation_mode(self, base_view):
        """Test setting simulation modes."""
        # Test left mode
        base_view.set_simulation_mode("left")
        assert base_view.current_mode == "left"

        # Test right mode
        base_view.set_simulation_mode("right")
        assert base_view.current_mode == "right"

        # Test relax mode
        base_view.set_simulation_mode("relax")
        assert base_view.current_mode == "relax"

    def test_resize_event(self, base_view):
        """Test resize event handling."""

        # Resize the view
        base_view.resize(1000, 800)

        # Check that spacers were updated (this tests the resizeEvent logic)
        # The exact values depend on the window width, but they should be non-zero
        assert base_view._center_spacer.width() > 0
        assert base_view._right_spacer.width() > 0

    def test_key_press_events(self, base_view, qtbot):
        """Test keyboard shortcuts for simulation."""
        # Test key 1 (left hand)
        qtbot.keyPress(base_view, Qt.Key.Key_1)
        assert base_view.current_mode == "left"

        # Test key 2 (right hand)
        qtbot.keyPress(base_view, Qt.Key.Key_2)
        assert base_view.current_mode == "right"

        # Test key 3 (relax)
        qtbot.keyPress(base_view, Qt.Key.Key_3)
        assert base_view.current_mode == "relax"

    def test_set_status(self, base_view):
        """Test setting status (for controller compatibility)."""
        base_view.set_status("Test Status")
        assert base_view.status_label.text() == "Test Status"


class TestTextCommandsExperimentView:
    """Test suite for the TextCommandsExperimentView class."""

    @pytest.fixture
    def text_view(self, qtbot: QtBot):
        """Create a TextCommandsExperimentView instance for testing."""
        view = TextCommandsExperimentView("Text Commands")
        qtbot.addWidget(view)
        return view

    def test_init(self, text_view):
        """Test text commands view initialization."""
        assert text_view.experiment_name == "Text Commands"
        assert text_view.center_content is not None

    def test_center_content_has_text(self, text_view):
        """Test that center content contains the expected text."""
        # Find QLabel in center content
        labels = text_view.center_content.findChildren(QLabel)
        text_label = None
        for label in labels:
            if hasattr(label, "text"):
                text_label = label
                break

        assert text_label is not None
        assert "Command: RELAX" in text_label.text()
        assert "Please follow the instructions" in text_label.text()


class TestAvatarExperimentView:
    """Test suite for the AvatarExperimentView class."""

    @pytest.fixture
    def avatar_view(self, qtbot: QtBot):
        """Create an AvatarExperimentView instance for testing."""
        view = AvatarExperimentView("Avatar")
        qtbot.addWidget(view)
        return view

    def test_init(self, avatar_view):
        """Test avatar view initialization."""
        assert avatar_view.experiment_name == "Avatar"
        assert avatar_view.center_content is not None

    def test_center_content_has_placeholder(self, avatar_view):
        """Test that center content contains avatar area and arm label."""
        labels = avatar_view.center_content.findChildren(QLabel)
        avatar_label = None
        arm_label = None

        for label in labels:
            if hasattr(label, "text") and "Relax" in label.text():
                arm_label = label
            elif avatar_label is None:  # First label is avatar label
                avatar_label = label

        # Avatar should start in relax mode (no image, just arm label)
        assert avatar_label is not None
        assert arm_label is not None
        assert "Relax" in arm_label.text()
        # In relax mode, avatar should not have a pixmap (image cleared)
        assert avatar_label.pixmap() is None or avatar_label.pixmap().isNull()

    def test_show_left_hand_content(self, avatar_view):
        """Test showing left hand avatar content."""
        avatar_view._show_left_hand_content()
        # Check that arm label was updated
        assert "Left Arm" in avatar_view.arm_label.text()

    def test_show_right_hand_content(self, avatar_view):
        """Test showing right hand avatar content."""
        avatar_view._show_right_hand_content()
        # Check that arm label was updated
        assert "Right Arm" in avatar_view.arm_label.text()

    def test_show_relax_content(self, avatar_view):
        """Test showing relax avatar content."""
        # First set to left hand
        avatar_view._show_left_hand_content()
        assert "Left Arm" in avatar_view.arm_label.text()

        # Then set to relax
        avatar_view._show_relax_content()
        assert "Relax" in avatar_view.arm_label.text()
        # Avatar should be cleared
        assert (
            avatar_view.avatar_label.pixmap() is None or avatar_view.avatar_label.pixmap().isNull()
        )


class TestVideoExperimentView:
    """Test suite for the VideoExperimentView class."""

    @pytest.fixture
    def video_view(self, qtbot: QtBot):
        """Create a VideoExperimentView instance for testing."""
        view = VideoExperimentView("Video")
        qtbot.addWidget(view)
        return view

    def test_init(self, video_view):
        """Test video view initialization."""
        assert video_view.experiment_name == "Video"
        assert video_view.center_content is not None

    def test_center_content_has_placeholder(self, video_view):
        """Test that center content contains video player and arm label."""
        # Check that video player and widget exist
        assert hasattr(video_view, "video_player")
        assert hasattr(video_view, "video_widget")
        assert video_view.video_player is not None
        assert video_view.video_widget is not None

        # Check that arm label exists and has correct initial text
        labels = video_view.center_content.findChildren(QLabel)
        arm_label = None
        for label in labels:
            if hasattr(label, "text") and "Left Arm" in label.text():
                arm_label = label
                break

        assert arm_label is not None
        assert "Left Arm" in arm_label.text()

    def test_show_left_hand_content(self, video_view):
        """Test showing left hand video content."""
        video_view._show_left_hand_content()
        # Check that arm label was updated
        assert "Left Arm" in video_view.arm_label.text()

    def test_show_right_hand_content(self, video_view):
        """Test showing right hand video content."""
        video_view._show_right_hand_content()
        # Check that arm label was updated
        assert "Right Arm" in video_view.arm_label.text()

    def test_show_relax_content(self, video_view):
        """Test showing relax video content."""
        # First set to left hand
        video_view._show_left_hand_content()
        assert "Left Arm" in video_view.arm_label.text()

        # Then set to relax
        video_view._show_relax_content()
        assert "Relax" in video_view.arm_label.text()

    def test_video_preloading(self, video_view):
        """Test that video files are preloaded on initialization."""
        assert hasattr(video_view, "left_video_path")
        assert hasattr(video_view, "right_video_path")
        assert hasattr(video_view, "left_video_exists")
        assert hasattr(video_view, "right_video_exists")
        # Check that paths contain expected video files
        assert "l_hand.mp4" in video_view.left_video_path
        assert "r_hand.mp4" in video_view.right_video_path


class TestBCIWorker:
    """Test suite for the BCIWorker class."""

    @pytest.fixture
    def bci_worker(self):
        """Create a BCIWorker instance for testing."""
        config = {"selected_electrodes": {14, 15, 16}, "output_path": "test/output"}  # C3, CZ, C4
        return BCIWorker("test/output", config)

    def test_init(self, bci_worker):
        """Test BCIWorker initialization."""
        assert bci_worker.output_path == "test/output"
        assert bci_worker.bci_config["selected_electrodes"] == {14, 15, 16}
        assert bci_worker._running is False
        assert bci_worker.raw_samples == []
        assert bci_worker.start_time is None

    @patch("airobo_trainer.models.bci_core.BCIEngine")
    def test_run_and_stop(self, mock_engine_class, bci_worker):
        """Test running and stopping the BCI worker."""
        mock_engine = Mock()
        mock_engine_class.return_value = mock_engine

        # Start the worker
        bci_worker._running = True
        bci_worker.start_time = Mock()

        # Test handle_raw_block
        test_block = np.array([[1, 2, 3], [4, 5, 6]])
        bci_worker.handle_raw_block(test_block)
        assert len(bci_worker.raw_samples) == 1

        # Test stop recording
        with patch("os.makedirs"), patch("builtins.open", mock_open()), patch(
            "csv.writer"
        ):
            bci_worker.stop_recording()
            assert bci_worker._running is False

    @patch("os.makedirs")
    @patch("builtins.open", new_callable=mock_open)
    @patch("csv.writer")
    def test_save_csv(self, mock_csv_writer, mock_file, mock_makedirs, bci_worker):
        """Test CSV saving functionality."""
        # Add some test data
        bci_worker.raw_samples = [
            np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]),
            np.array([[7.0, 8.0, 9.0], [10.0, 11.0, 12.0]]),
        ]
        bci_worker.start_time = Mock()
        bci_worker.start_time.strftime.return_value = "test_timestamp"

        bci_worker._save_csv()

        # Verify CSV was written with correct headers and data
        mock_csv_writer.assert_called_once()
        writer_instance = mock_csv_writer.return_value
        # Should write header first, then all data rows
        assert writer_instance.writerow.call_count == 1  # Header
        assert writer_instance.writerows.call_count == 1  # All data rows
