"""
Unit tests for ExperimentConfigView
"""

import pytest
import os
import json
from unittest.mock import patch, MagicMock

from airobo_trainer.views.experiment_config_view import ExperimentConfigView


@pytest.fixture
def app(qapp):
    """Ensure QApplication exists."""
    return qapp


@pytest.fixture
def config_view(app):
    """Create an ExperimentConfigView instance."""
    view = ExperimentConfigView()
    yield view
    # Cleanup will be handled by atexit in the view itself


class TestExperimentConfigView:
    """Test suite for the ExperimentConfigView class."""

    def test_init(self, config_view):
        """Test config view initialization."""
        assert config_view.windowTitle() == "Experiment Configuration"
        assert hasattr(config_view, "left_text_edit")
        assert hasattr(config_view, "right_text_edit")
        assert hasattr(config_view, "relax_text_edit")
        assert hasattr(config_view, "left_avatar_edit")
        assert hasattr(config_view, "right_avatar_edit")
        assert hasattr(config_view, "relax_avatar_edit")
        assert hasattr(config_view, "left_video_edit")
        assert hasattr(config_view, "right_video_edit")
        assert hasattr(config_view, "relax_video_edit")

    def test_load_config_no_file(self, config_view):
        """Test loading config when no file exists."""
        config = config_view._load_config()
        assert config == {}

    def test_save_and_load_config(self, config_view):
        """Test saving and loading configuration."""
        test_config = {
            "left_text": "Test left",
            "right_text": "Test right",
            "relax_text": "Test relax",
            "left_avatar": "test_left.png",
            "right_avatar": "test_right.png",
            "relax_avatar": "test_relax.png",
            "left_video": "test_left.mp4",
            "right_video": "test_right.mp4",
            "relax_video": "test_relax.mp4",
        }

        # Save config
        config_view._save_configuration = lambda: config_view._save_config(test_config)
        config_view._save_config(test_config)

        # Load config
        loaded_config = config_view._load_config()
        assert loaded_config == test_config

    def test_load_current_assets_defaults(self, config_view):
        """Test loading default assets when no config exists."""
        config_view._load_current_assets()
        assert (
            config_view.left_text_edit.text()
            == "LEFT HAND\n\nImagine moving your left hand.\nFocus on the movement and muscle activation."
        )
        assert (
            config_view.right_text_edit.text()
            == "RIGHT HAND\n\nImagine moving your right hand.\nFocus on the movement and muscle activation."
        )
        assert (
            config_view.relax_text_edit.text()
            == "Command: RELAX\n\nPlease follow the instructions to control the system using your thoughts."
        )
        assert config_view.left_avatar_edit.text() == "l_hand.png"
        assert config_view.right_avatar_edit.text() == "r_hand.png"
        assert config_view.relax_avatar_edit.text() == ""
        assert config_view.left_video_edit.text() == "l_hand.mp4"
        assert config_view.right_video_edit.text() == "r_hand.mp4"
        assert config_view.relax_video_edit.text() == ""

    def test_load_current_assets_with_config(self, config_view):
        """Test loading assets from existing config."""
        # Create full paths for testing
        import os
        test_image_path = "/path/to/custom_left.png"
        test_video_path = "/path/to/custom_left.mp4"

        test_config = {
            "left_text": "Custom left",
            "right_text": "Custom right",
            "relax_text": "Custom relax",
            "left_avatar": test_image_path,
            "right_avatar": "custom_right.png",
            "relax_avatar": "custom_relax.png",
            "left_video": test_video_path,
            "right_video": "custom_right.mp4",
            "relax_video": "custom_relax.mp4",
        }

        # Save test config
        config_view._save_config(test_config)

        # Load current assets
        config_view._load_current_assets()

        assert config_view.left_text_edit.text() == "Custom left"
        assert config_view.right_text_edit.text() == "Custom right"
        assert config_view.relax_text_edit.text() == "Custom relax"
        assert config_view.left_avatar_edit.text() == test_image_path
        assert config_view.right_avatar_edit.text() == "custom_right.png"
        assert config_view.relax_avatar_edit.text() == "custom_relax.png"
        assert config_view.left_video_edit.text() == test_video_path
        assert config_view.right_video_edit.text() == "custom_right.mp4"
        assert config_view.relax_video_edit.text() == "custom_relax.mp4"

    @patch("airobo_trainer.views.experiment_config_view.QFileDialog")
    @patch("airobo_trainer.views.experiment_config_view.shutil.copy2")
    @patch("os.path.exists", return_value=True)
    def test_upload_text_file_success(self, mock_exists, mock_copy, mock_qfd, config_view):
        """Test successful text file upload."""
        # Mock file dialog
        mock_dialog = MagicMock()
        mock_qfd.return_value = mock_dialog
        mock_dialog.exec.return_value = True
        mock_dialog.selectedFiles.return_value = ["/path/to/test.txt"]

        # Mock file reading
        with patch("builtins.open", create=True) as mock_open:
            mock_file = MagicMock()
            mock_file.read.return_value = "Test content"
            mock_open.return_value.__enter__.return_value = mock_file

            # Call upload method
            config_view._upload_text_file("left")

            # Check that text was set
            assert config_view.left_text_edit.text() == "Test content"
            assert config_view.status_label.text() == "Loaded text file for left"

    @patch("airobo_trainer.views.experiment_config_view.QFileDialog")
    @patch("airobo_trainer.views.experiment_config_view.shutil.copy2")
    @patch("os.path.exists", return_value=True)
    def test_upload_image_file_success(self, mock_exists, mock_copy, mock_qfd, config_view):
        """Test successful image file upload."""
        # Mock file dialog
        mock_dialog = MagicMock()
        mock_qfd.return_value = mock_dialog
        mock_dialog.exec.return_value = True
        mock_dialog.selectedFiles.return_value = ["/path/to/test.png"]

        # Call upload method
        config_view._upload_image_file("left")

        # Check that filename was set
        assert config_view.left_avatar_edit.text() == "test.png"
        assert "Uploaded image for left: test.png" in config_view.status_label.text()

        # Check that copy was called
        mock_copy.assert_called_once()

    @patch("airobo_trainer.views.experiment_config_view.QFileDialog")
    @patch("airobo_trainer.views.experiment_config_view.shutil.copy2")
    @patch("os.path.exists", return_value=True)
    def test_upload_video_file_success(self, mock_exists, mock_copy, mock_qfd, config_view):
        """Test successful video file upload."""
        # Mock file dialog
        mock_dialog = MagicMock()
        mock_qfd.return_value = mock_dialog
        mock_dialog.exec.return_value = True
        mock_dialog.selectedFiles.return_value = ["/path/to/test.mp4"]

        # Call upload method
        config_view._upload_video_file("left")

        # Check that filename was set
        assert config_view.left_video_edit.text() == "test.mp4"
        assert "Uploaded video for left: test.mp4" in config_view.status_label.text()

        # Check that copy was called
        mock_copy.assert_called_once()

    @patch("airobo_trainer.views.experiment_config_view.QMessageBox")
    def test_upload_text_file_error(self, mock_qmsgbox, config_view):
        """Test text file upload error handling."""
        with patch("builtins.open", side_effect=Exception("Read error")):
            with patch("airobo_trainer.views.experiment_config_view.QFileDialog") as mock_qfd:
                mock_dialog = MagicMock()
                mock_qfd.return_value = mock_dialog
                mock_dialog.exec.return_value = True
                mock_dialog.selectedFiles.return_value = ["/path/to/test.txt"]

                config_view._upload_text_file("left")

                # Check that error message was shown
                mock_qmsgbox.warning.assert_called_once()

    @patch("airobo_trainer.views.experiment_config_view.QMessageBox")
    def test_upload_image_file_error(self, mock_qmsgbox, config_view):
        """Test image file upload error handling."""
        with patch(
            "airobo_trainer.views.experiment_config_view.shutil.copy2",
            side_effect=Exception("Copy error"),
        ):
            with patch("airobo_trainer.views.experiment_config_view.QFileDialog") as mock_qfd:
                mock_dialog = MagicMock()
                mock_qfd.return_value = mock_dialog
                mock_dialog.exec.return_value = True
                mock_dialog.selectedFiles.return_value = ["/path/to/test.png"]

                config_view._upload_image_file("left")

                # Check that error message was shown
                mock_qmsgbox.warning.assert_called_once()

    @patch("airobo_trainer.views.experiment_config_view.QMessageBox")
    def test_upload_video_file_error(self, mock_qmsgbox, config_view):
        """Test video file upload error handling."""
        with patch(
            "airobo_trainer.views.experiment_config_view.shutil.copy2",
            side_effect=Exception("Copy error"),
        ):
            with patch("airobo_trainer.views.experiment_config_view.QFileDialog") as mock_qfd:
                mock_dialog = MagicMock()
                mock_qfd.return_value = mock_dialog
                mock_dialog.exec.return_value = True
                mock_dialog.selectedFiles.return_value = ["/path/to/test.mp4"]

                config_view._upload_video_file("left")

                # Check that error message was shown
                mock_qmsgbox.warning.assert_called_once()

    @patch("airobo_trainer.views.experiment_config_view.QMessageBox")
    def test_save_configuration_success(self, mock_qmsgbox, config_view):
        """Test successful configuration save."""
        # Set some test values
        config_view.left_text_edit.setText("Test left")
        config_view.right_text_edit.setText("Test right")
        config_view.relax_text_edit.setText("Test relax")
        config_view.left_avatar_edit.setText("test_left.png")
        config_view.right_avatar_edit.setText("test_right.png")
        config_view.relax_avatar_edit.setText("test_relax.png")
        config_view.left_video_edit.setText("test_left.mp4")
        config_view.right_video_edit.setText("test_right.mp4")
        config_view.relax_video_edit.setText("test_relax.mp4")

        # Save configuration
        config_view._save_configuration()

        # Check that success message was shown
        mock_qmsgbox.information.assert_called_once()

        # Check that config file was created in persistent directory
        config_file = config_view.config_file
        assert os.path.exists(config_file)

        # Check file contents
        with open(config_file, "r") as f:
            saved_config = json.load(f)

        expected_config = {
            "left_text": "Test left",
            "right_text": "Test right",
            "relax_text": "Test relax",
            "left_avatar": "test_left.png",
            "right_avatar": "test_right.png",
            "relax_avatar": "test_relax.png",
            "left_video": "test_left.mp4",
            "right_video": "test_right.mp4",
            "relax_video": "test_relax.mp4",
        }
        assert saved_config == expected_config

    def test_get_experiment_config_no_file(self):
        """Test getting config when no file exists."""
        config = ExperimentConfigView.get_experiment_config()
        assert config == {}

    def test_get_experiment_config_with_file(self, config_view):
        """Test getting config from existing file."""
        test_config = {"test_key": "test_value"}
        config_view._save_config(test_config)

        loaded_config = ExperimentConfigView.get_experiment_config()
        assert loaded_config == test_config

    def test_back_button_signal(self, config_view):
        """Test back button signal emission."""
        signal_received = False

        def signal_handler():
            nonlocal signal_received
            signal_received = True

        config_view.back_requested.connect(signal_handler)
        config_view._on_back_button_clicked()

        assert signal_received

    def test_set_status(self, config_view):
        """Test setting status label."""
        test_message = "Test status message"
        config_view.set_status(test_message)
        assert config_view.status_label.text() == test_message

    def test_persistent_config_across_instances(self, config_view):
        """Test that config persists across different view instances."""
        # Save config in first instance
        test_config = {
            "left_text": "Persistent left",
            "right_text": "Persistent right",
            "relax_text": "Persistent relax",
        }
        config_view._save_config(test_config)

        # Create new instance and check if it loads the same config
        new_config_view = ExperimentConfigView()
        loaded_config = new_config_view._load_config()

        assert loaded_config == test_config

        # Also test static method
        static_config = ExperimentConfigView.get_experiment_config()
        assert static_config == test_config

    def test_missing_files_warning(self, capsys):
        """Test that warnings are shown for missing files."""
        # Configure custom files that don't exist
        test_config = {
            "left_avatar": "missing_left.png",
            "right_avatar": "missing_right.png",
            "relax_avatar": "missing_relax.png",
            "left_video": "missing_left.mp4",
            "right_video": "missing_right.mp4",
            "relax_video": "missing_relax.mp4",
        }

        # Create avatar view with missing files - this should trigger warnings
        from airobo_trainer.views.experiment_views import AvatarExperimentView
        with patch('airobo_trainer.views.experiment_config_view.ExperimentConfigView.get_experiment_config', return_value=test_config):
            avatar_view = AvatarExperimentView("Avatar")

        # Check that warnings were printed (captured by capsys)
        captured = capsys.readouterr()
        assert "Warning: Custom left avatar 'missing_left.png' not found" in captured.out
        assert "Warning: Custom right avatar 'missing_right.png' not found" in captured.out
        assert "Warning: Custom relax avatar 'missing_relax.png' not found" in captured.out


class TestAvatarExperimentView:
    """Test suite for the AvatarExperimentView preloading."""

    @pytest.fixture
    def avatar_view(self, qtbot):
        """Create an AvatarExperimentView instance for testing."""
        from airobo_trainer.views.experiment_views import AvatarExperimentView

        view = AvatarExperimentView("Avatar")
        qtbot.addWidget(view)
        return view

    def test_initialization(self, avatar_view):
        """Test that avatar view initializes correctly."""
        # Check that experiment config is loaded
        assert hasattr(avatar_view, "experiment_config")
        assert isinstance(avatar_view.experiment_config, dict)

        # Check that view starts in relax mode
        assert avatar_view.current_mode == "relax"


class TestVideoExperimentView:
    """Test suite for the VideoExperimentView preloading."""

    @pytest.fixture
    def video_view(self, qtbot):
        """Create a VideoExperimentView instance for testing."""
        from airobo_trainer.views.experiment_views import VideoExperimentView

        view = VideoExperimentView("Video")
        qtbot.addWidget(view)
        return view

    def test_initialization(self, video_view):
        """Test that video view initializes correctly."""
        # Check that experiment config is loaded
        assert hasattr(video_view, "experiment_config")
        assert isinstance(video_view.experiment_config, dict)

        # Check that view starts in relax mode
        assert video_view.current_mode == "relax"
