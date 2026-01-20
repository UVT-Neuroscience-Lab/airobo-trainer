"""
Experiment Configuration View - Experiment Assets Configuration Interface
Follows the View component of MVC architecture
"""

from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QGroupBox,
    QHBoxLayout,
    QLineEdit,
    QFileDialog,
    QMessageBox,
)
from PyQt6.QtCore import Qt, pyqtSignal
import os
import json


class ExperimentConfigView(QMainWindow):
    """
    Experiment Configuration View - Interface for configuring experiment assets.

    This class handles the experiment configuration UI including asset uploads
    for different experiment types and modes.
    """

    # Custom signals
    back_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        # Persistent config file in project assets directory
        self.config_dir = os.path.join(os.path.dirname(__file__), "..", "assets", "configs")
        os.makedirs(self.config_dir, exist_ok=True)
        self.config_file = os.path.join(self.config_dir, "experiment_config.json")

        self._init_ui()
        self._load_current_assets()



    def _init_ui(self):
        """Set up the experiment configuration interface."""
        self.setWindowTitle("Experiment Configuration")
        self.setMinimumSize(700, 600)

        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Back button at the top
        back_button = QPushButton("← Back")
        back_button.clicked.connect(self._on_back_button_clicked)
        main_layout.addWidget(back_button, alignment=Qt.AlignmentFlag.AlignLeft)

        # Text Commands Configuration section
        text_group = QGroupBox("Text Commands")
        text_layout = QVBoxLayout(text_group)

        # Left hand text
        left_text_layout = QHBoxLayout()
        left_text_layout.addWidget(QLabel("Left Hand:"))
        self.left_text_edit = QLineEdit()
        self.left_text_edit.setPlaceholderText(
            "Imagine moving your left hand.\nFocus on the movement and muscle activation."
        )
        left_text_layout.addWidget(self.left_text_edit)
        left_text_button = QPushButton("Upload Text File")
        left_text_button.clicked.connect(lambda: self._upload_text_file("left"))
        left_text_layout.addWidget(left_text_button)
        text_layout.addLayout(left_text_layout)

        # Right hand text
        right_text_layout = QHBoxLayout()
        right_text_layout.addWidget(QLabel("Right Hand:"))
        self.right_text_edit = QLineEdit()
        self.right_text_edit.setPlaceholderText(
            "Imagine moving your right hand.\nFocus on the movement and muscle activation."
        )
        right_text_layout.addWidget(self.right_text_edit)
        right_text_button = QPushButton("Upload Text File")
        right_text_button.clicked.connect(lambda: self._upload_text_file("right"))
        right_text_layout.addWidget(right_text_button)
        text_layout.addLayout(right_text_layout)

        # Relax text
        relax_text_layout = QHBoxLayout()
        relax_text_layout.addWidget(QLabel("Relax:"))
        self.relax_text_edit = QLineEdit()
        self.relax_text_edit.setPlaceholderText(
            "Please follow the instructions to control the system using your thoughts."
        )
        relax_text_layout.addWidget(self.relax_text_edit)
        relax_text_button = QPushButton("Upload Text File")
        relax_text_button.clicked.connect(lambda: self._upload_text_file("relax"))
        relax_text_layout.addWidget(relax_text_button)
        text_layout.addLayout(relax_text_layout)

        main_layout.addWidget(text_group)

        # Avatar Images Configuration section
        avatar_group = QGroupBox("Avatar Images")
        avatar_layout = QVBoxLayout(avatar_group)

        # Left hand avatar
        left_avatar_layout = QHBoxLayout()
        left_avatar_layout.addWidget(QLabel("Left Hand:"))
        self.left_avatar_edit = QLineEdit()
        self.left_avatar_edit.setPlaceholderText("l_hand.png")
        left_avatar_layout.addWidget(self.left_avatar_edit)
        left_avatar_button = QPushButton("Upload Image")
        left_avatar_button.clicked.connect(lambda: self._upload_image_file("left"))
        left_avatar_layout.addWidget(left_avatar_button)
        avatar_layout.addLayout(left_avatar_layout)

        # Right hand avatar
        right_avatar_layout = QHBoxLayout()
        right_avatar_layout.addWidget(QLabel("Right Hand:"))
        self.right_avatar_edit = QLineEdit()
        self.right_avatar_edit.setPlaceholderText("r_hand.png")
        right_avatar_layout.addWidget(self.right_avatar_edit)
        right_avatar_button = QPushButton("Upload Image")
        right_avatar_button.clicked.connect(lambda: self._upload_image_file("right"))
        right_avatar_layout.addWidget(right_avatar_button)
        avatar_layout.addLayout(right_avatar_layout)

        # Relax avatar (optional)
        relax_avatar_layout = QHBoxLayout()
        relax_avatar_layout.addWidget(QLabel("Relax:"))
        self.relax_avatar_edit = QLineEdit()
        self.relax_avatar_edit.setPlaceholderText("(empty)")
        relax_avatar_layout.addWidget(self.relax_avatar_edit)
        relax_avatar_button = QPushButton("Upload Image")
        relax_avatar_button.clicked.connect(lambda: self._upload_image_file("relax"))
        relax_avatar_layout.addWidget(relax_avatar_button)
        avatar_layout.addLayout(relax_avatar_layout)

        main_layout.addWidget(avatar_group)

        # Video Configuration section
        video_group = QGroupBox("Videos")
        video_layout = QVBoxLayout(video_group)

        # Left hand video
        left_video_layout = QHBoxLayout()
        left_video_layout.addWidget(QLabel("Left Hand:"))
        self.left_video_edit = QLineEdit()
        self.left_video_edit.setPlaceholderText("l_hand.mp4")
        left_video_layout.addWidget(self.left_video_edit)
        left_video_button = QPushButton("Upload Video")
        left_video_button.clicked.connect(lambda: self._upload_video_file("left"))
        left_video_layout.addWidget(left_video_button)
        video_layout.addLayout(left_video_layout)

        # Right hand video
        right_video_layout = QHBoxLayout()
        right_video_layout.addWidget(QLabel("Right Hand:"))
        self.right_video_edit = QLineEdit()
        self.right_video_edit.setPlaceholderText("r_hand.mp4")
        right_video_layout.addWidget(self.right_video_edit)
        right_video_button = QPushButton("Upload Video")
        right_video_button.clicked.connect(lambda: self._upload_video_file("right"))
        right_video_layout.addWidget(right_video_button)
        video_layout.addLayout(right_video_layout)

        # Relax video (optional)
        relax_video_layout = QHBoxLayout()
        relax_video_layout.addWidget(QLabel("Relax:"))
        self.relax_video_edit = QLineEdit()
        self.relax_video_edit.setPlaceholderText("(empty)")
        relax_video_layout.addWidget(self.relax_video_edit)
        relax_video_button = QPushButton("Upload Video")
        relax_video_button.clicked.connect(lambda: self._upload_video_file("relax"))
        relax_video_layout.addWidget(relax_video_button)
        video_layout.addLayout(relax_video_layout)

        main_layout.addWidget(video_group)

        # Save button
        save_button = QPushButton("Save Configuration")
        save_button.clicked.connect(self._save_configuration)
        main_layout.addWidget(save_button, alignment=Qt.AlignmentFlag.AlignCenter)

        # Status label
        self.status_label = QLabel("Experiment Configuration Ready")
        self.status_label.setStyleSheet("color: gray; margin: 5px;")
        main_layout.addWidget(self.status_label)

    def _on_back_button_clicked(self):
        """Handle back button click."""
        self.back_requested.emit()

    def _upload_text_file(self, mode: str):
        """Upload a text file for the specified mode."""
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        file_dialog.setNameFilter("Text files (*.txt)")

        if file_dialog.exec():
            file_path = file_dialog.selectedFiles()[0]
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                if mode == "left":
                    self.left_text_edit.setText(content)
                elif mode == "right":
                    self.right_text_edit.setText(content)
                elif mode == "relax":
                    self.relax_text_edit.setText(content)
                self.status_label.setText(f"Loaded text file for {mode}")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to read text file: {e}")

    def _upload_image_file(self, mode: str):
        """Upload an image file for the specified mode."""
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        file_dialog.setNameFilter("Image files (*.png *.jpg *.jpeg *.bmp *.gif)")

        if file_dialog.exec():
            file_path = file_dialog.selectedFiles()[0]

            # Save full path in config
            if mode == "left":
                self.left_avatar_edit.setText(file_path)
            elif mode == "right":
                self.right_avatar_edit.setText(file_path)
            elif mode == "relax":
                self.relax_avatar_edit.setText(file_path)
            filename = os.path.basename(file_path)
            self.status_label.setText(f"Selected image for {mode}: {filename}")

    def _upload_video_file(self, mode: str):
        """Upload a video file for the specified mode."""
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        file_dialog.setNameFilter("Video files (*.mp4 *.avi *.mov *.wmv)")

        if file_dialog.exec():
            file_path = file_dialog.selectedFiles()[0]

            # Save full path in config
            if mode == "left":
                self.left_video_edit.setText(file_path)
            elif mode == "right":
                self.right_video_edit.setText(file_path)
            elif mode == "relax":
                self.relax_video_edit.setText(file_path)
            filename = os.path.basename(file_path)
            self.status_label.setText(f"Selected video for {mode}: {filename}")

    def _load_current_assets(self):
        """Load current asset configurations."""
        config = self._load_config()
        self.left_text_edit.setText(
            config.get(
                "left_text",
                "LEFT HAND\n\nImagine moving your left hand.\nFocus on the movement and muscle activation.",
            )
        )
        self.right_text_edit.setText(
            config.get(
                "right_text",
                "RIGHT HAND\n\nImagine moving your right hand.\nFocus on the movement and muscle activation.",
            )
        )
        self.relax_text_edit.setText(
            config.get(
                "relax_text",
                "Command: RELAX\n\nPlease follow the instructions to control the system using your thoughts.",
            )
        )
        self.left_avatar_edit.setText(config.get("left_avatar", "l_hand.png"))
        self.right_avatar_edit.setText(config.get("right_avatar", "r_hand.png"))
        self.relax_avatar_edit.setText(config.get("relax_avatar", ""))
        self.left_video_edit.setText(config.get("left_video", "l_hand.mp4"))
        self.right_video_edit.setText(config.get("right_video", "r_hand.mp4"))
        self.relax_video_edit.setText(config.get("relax_video", ""))

    def _load_config(self):
        """Load configuration from file."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading config: {e}")
        return {}

    def _save_configuration(self):
        """Save the current configuration."""
        config = {
            "left_text": self.left_text_edit.text(),
            "right_text": self.right_text_edit.text(),
            "relax_text": self.relax_text_edit.text(),
            "left_avatar": self.left_avatar_edit.text(),
            "right_avatar": self.right_avatar_edit.text(),
            "relax_avatar": self.relax_avatar_edit.text(),
            "left_video": self.left_video_edit.text(),
            "right_video": self.right_video_edit.text(),
            "relax_video": self.relax_video_edit.text(),
        }
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, "w") as f:
                json.dump(config, f, indent=2)
            self.status_label.setText("Configuration saved successfully")
            QMessageBox.information(self, "Success", "Experiment configuration has been saved.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to save configuration: {e}")

    def _save_config(self, config):
        """Save a config dictionary to file (helper method for testing)."""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, "w") as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            raise e

    @staticmethod
    def get_experiment_config():
        """Get the current experiment configuration from persistent storage."""
        config_dir = os.path.join(os.path.dirname(__file__), "..", "assets", "configs")
        config_file = os.path.join(config_dir, "experiment_config.json")

        if os.path.exists(config_file):
            try:
                with open(config_file, "r") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading persistent config: {e}")
        return {}



    def set_status(self, message: str):
        """Set the status label text."""
        self.status_label.setText(message)
