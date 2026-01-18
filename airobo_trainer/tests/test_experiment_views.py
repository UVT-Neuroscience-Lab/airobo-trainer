"""
Unit tests for Experiment Views
"""

import pytest
from pytestqt.qtbot import QtBot
from PyQt6.QtWidgets import QPushButton, QLabel

from airobo_trainer.views.experiment_views import (
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
        assert "Please follow the voice instructions" in text_label.text()


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
        """Test that center content contains avatar image."""
        labels = avatar_view.center_content.findChildren(QLabel)
        avatar_label = None
        for label in labels:
            avatar_label = label
            break

        assert avatar_label is not None
        # Check if pixmap is set (image loaded) or fallback text is shown
        if avatar_label.pixmap() is not None:
            # Image was loaded successfully
            assert avatar_label.pixmap().isNull() is False
        else:
            # Fallback text is shown
            assert "Avatar Image" in avatar_label.text()
            assert "l_hand.png" in avatar_label.text()


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
        """Test that center content contains video placeholder."""
        labels = video_view.center_content.findChildren(QLabel)
        placeholder_label = None
        for label in labels:
            if hasattr(label, "text"):
                placeholder_label = label
                break

        assert placeholder_label is not None
        assert "Video Area" in placeholder_label.text()
        assert "Video will be played here" in placeholder_label.text()
