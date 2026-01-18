"""
Experiment Views - Views for different experiment types
Follows the View component of MVC architecture
"""

from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QSizePolicy,
)
from PyQt6.QtCore import Qt, pyqtSignal, QRect
from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QPixmap


class MuscleBar(QFrame):
    """
    Custom widget showing a vertical muscle activation bar with 6 segments.
    """

    def __init__(self, arm_name: str):
        super().__init__()
        self.arm_name = arm_name
        self.activation_levels = [0] * 6  # 6 segments, 0-100 activation
        self.setMinimumSize(100, 300)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        self.setFrameStyle(QFrame.Shape.Box)

    def set_activation(self, segment: int, level: int):
        """Set activation level for a specific segment (0-100)."""
        if 0 <= segment < 6:
            self.activation_levels[segment] = max(0, min(100, level))
            self.update()

    def paintEvent(self, event):
        """Paint the muscle activation bar."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw white background with black border for the entire widget
        painter.fillRect(self.rect(), QColor(255, 255, 255))
        painter.setPen(QPen(QColor(0, 0, 0), 2))
        painter.drawRect(self.rect().adjusted(1, 1, -1, -1))

        # Calculate space for the light blue label at the top
        label_height = 30
        label_y = 5
        label_rect = QRect(5, label_y, self.width() - 10, label_height)

        # Light blue background for label (separate from main white background)
        painter.fillRect(label_rect, QColor(173, 216, 230))  # Light blue
        painter.setPen(QPen(QColor(0, 0, 0), 1))
        painter.drawRect(label_rect)

        # Draw text with larger, bold font
        font = QFont(painter.font())
        font.setPointSize(11)
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(QColor(0, 0, 0))
        painter.drawText(label_rect, Qt.AlignmentFlag.AlignCenter, self.arm_name)

        # Calculate space for the activation bars (below the label)
        bar_start_y = label_y + label_height + 10
        bar_available_height = self.height() - bar_start_y - 10

        bar_width = 50
        bar_height = min(200, bar_available_height)  # Use available space, max 200
        bar_x = (self.width() - bar_width) // 2
        bar_y = (
            bar_start_y + (bar_available_height - bar_height) // 2
        )  # Center vertically in available space

        segment_height = bar_height // 6

        # Draw segments from bottom to top (anatomical order)
        for i in range(6):
            segment_y = bar_y + bar_height - (i + 1) * segment_height
            activation = self.activation_levels[i]

            # Color based on activation level
            if activation > 70:
                color = QColor(0, 255, 0)  # Green for high activation
            elif activation > 40:
                color = QColor(255, 255, 0)  # Yellow for medium activation
            else:
                color = QColor(128, 128, 128)  # Gray for low activation (initial state)

            painter.fillRect(bar_x, segment_y, bar_width, segment_height, color)

            # Draw segment border
            painter.setPen(QPen(QColor(0, 0, 0), 1))
            painter.drawRect(bar_x, segment_y, bar_width, segment_height)


class BaseExperimentView(QMainWindow):
    """
    Base class for experiment views.

    This class provides common functionality for all experiment types
    including back navigation and muscle activation bars.
    """

    # Custom signals
    back_requested = pyqtSignal()

    def __init__(self, experiment_name: str):
        super().__init__()
        self.experiment_name = experiment_name
        self._init_ui()

    def _init_ui(self):
        """Set up the basic experiment interface."""
        self.setWindowTitle(f"AiRobo-Trainer - {self.experiment_name}")
        self.setMinimumSize(900, 700)

        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Back button at the top
        back_button = QPushButton("← Back")
        back_button.clicked.connect(self._on_back_button_clicked)
        back_button.setMaximumWidth(100)
        main_layout.addWidget(back_button, alignment=Qt.AlignmentFlag.AlignLeft)

        # Experiment title right underneath back button
        title_label = QLabel(self.experiment_name)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(
            "font-size: 24px; font-weight: bold; margin: 15px 0 20px 0; color: #FFF;"
        )
        main_layout.addWidget(title_label)

        # Create horizontal layout for content with edge-positioned bars
        content_layout = QHBoxLayout()
        content_layout.setSpacing(0)

        # Left muscle bar (at leftmost edge)
        self.left_arm_bar = MuscleBar("Left Arm")
        self.left_arm_bar.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        content_layout.addWidget(self.left_arm_bar, 0)  # No stretch

        # Center spacer (10% of width)
        center_spacer = QWidget()
        center_spacer.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        center_spacer.setMinimumWidth(0)  # Will be set dynamically
        content_layout.addWidget(center_spacer, 0)  # No stretch, fixed width

        # Center content area (takes remaining space)
        self.center_content = self._create_center_content()
        self.center_content.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        content_layout.addWidget(self.center_content, 1)  # Takes remaining space

        # Right spacer (10% of width)
        right_spacer = QWidget()
        right_spacer.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        right_spacer.setMinimumWidth(0)  # Will be set dynamically
        content_layout.addWidget(right_spacer, 0)  # No stretch, fixed width

        # Right muscle bar (at rightmost edge)
        self.right_arm_bar = MuscleBar("Right Arm")
        self.right_arm_bar.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        content_layout.addWidget(self.right_arm_bar, 0)  # No stretch

        main_layout.addLayout(content_layout, 1)  # Give content layout stretch factor

        # Store references to spacers for resize handling
        self._center_spacer = center_spacer
        self._right_spacer = right_spacer

    def resizeEvent(self, event):
        """Handle window resize to maintain percentage-based spacing."""
        super().resizeEvent(event)

        # Calculate available width for content area
        content_width = self.width() - 20  # Subtract margins

        # Calculate spacer widths (10% of content area)
        spacer_width = int(content_width * 0.10)

        # Set spacer widths
        self._center_spacer.setFixedWidth(spacer_width)
        self._right_spacer.setFixedWidth(spacer_width)

    def _create_center_content(self):
        """Create the center content widget. To be implemented by subclasses."""
        # Default implementation - empty widget with full-size styling
        widget = QWidget()
        widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        widget.setStyleSheet("""
            QWidget {
                background-color: #e0e0e0;
                border: 1px solid #999;
                border-radius: 8px;
                margin: 2%;
                width: 96%;
                height: 96%;
            }
        """)
        return widget

    def _on_back_button_clicked(self):
        """Handle back button click."""
        self.back_requested.emit()

    def update_muscle_activation(self, arm: str, segment: int, level: int):
        """
        Update muscle activation level.

        Args:
            arm: "left" or "right"
            segment: 0-5 (from bottom to top)
            level: 0-100 activation level
        """
        if arm.lower() == "left":
            self.left_arm_bar.set_activation(segment, level)
        elif arm.lower() == "right":
            self.right_arm_bar.set_activation(segment, level)


class TextCommandsExperimentView(BaseExperimentView):
    """
    Experiment view for Text Commands training.
    Shows text commands with background in the center.
    """

    def _create_center_content(self):
        """Create center content with text display."""
        widget = QWidget()
        widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        widget.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
                border: 2px solid #ccc;
                border-radius: 10px;
                margin: 5% 2%;
                width: 96%;
                height: 90%;
                padding: 5% 3% 5% 3%;
            }
        """)
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)

        # Text display area with word wrapping
        text_label = QLabel(
            "Command: RELAX\n\nPlease follow the voice instructions to control the system using your thoughts."
        )
        text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        text_label.setWordWrap(True)  # Enable word wrapping
        text_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #333;
                line-height: 1.4;
            }
        """)
        layout.addWidget(text_label, alignment=Qt.AlignmentFlag.AlignCenter)

        return widget


class AvatarExperimentView(BaseExperimentView):
    """
    Experiment view for Avatar training.
    Shows placeholder for avatar image in the center.
    """

    def _create_center_content(self):
        """Create center content with avatar image."""
        widget = QWidget()
        widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        widget.setStyleSheet("""
            QWidget {
                background-color: #e0e0e0;
                border: 2px dashed #999;
                border-radius: 10px;
                margin: 5% 2%;
                width: 96%;
                height: 90%;
                padding: 2% 1% 2% 1%;
            }
        """)

        # Avatar image label that will be resized dynamically
        self.avatar_label = QLabel()
        self.avatar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.avatar_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.avatar_label.setMinimumSize(100, 100)

        # Load the l_hand.png image
        self.original_pixmap = QPixmap("airobo_trainer/assets/images/l_hand.png")
        if not self.original_pixmap.isNull():
            # Initial scaling will be done in resizeEvent
            self._scale_avatar_image()
        else:
            # Fallback if image can't be loaded
            self.avatar_label.setText("Avatar Image\n(Could not load l_hand.png)")
            self.avatar_label.setStyleSheet("font-size: 14px; color: #666;")

        layout = QVBoxLayout(widget)
        layout.addWidget(self.avatar_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Store widget reference for resize handling
        widget.avatar_widget = self
        return widget

    def _scale_avatar_image(self):
        """Scale the avatar image to fit the available space."""
        if hasattr(self, "original_pixmap") and not self.original_pixmap.isNull():
            # Get the size of the avatar label
            label_size = self.avatar_label.size()
            if (
                label_size.width() > 50 and label_size.height() > 50
            ):  # Ensure we have valid dimensions
                # Scale to fit while maintaining aspect ratio
                scaled_pixmap = self.original_pixmap.scaled(
                    label_size,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
                self.avatar_label.setPixmap(scaled_pixmap)

    def resizeEvent(self, event):
        """Handle window resize to rescale avatar image."""
        super().resizeEvent(event)
        # Rescale the avatar image when the window resizes
        if hasattr(self, "_scale_avatar_image"):
            self._scale_avatar_image()


class VideoExperimentView(BaseExperimentView):
    """
    Experiment view for Video training.
    Shows video area in the center, ready for video playback.
    """

    def _create_center_content(self):
        """Create center content with video area."""
        widget = QWidget()
        widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        widget.setStyleSheet("""
            QWidget {
                background-color: #000;
                border: 2px solid #333;
                border-radius: 5px;
                margin: 5% 2%;
                width: 96%;
                height: 90%;
                padding: 2% 1% 2% 1%;
            }
        """)

        # Video display area that will be resized dynamically when video is added
        self.video_label = QLabel("Video Area\n(Video will be played here)")
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.video_label.setMinimumSize(200, 150)
        self.video_label.setStyleSheet("""
            QLabel {
                background-color: #111;
                border: 1px solid #444;
                border-radius: 3px;
                color: #fff;
                font-size: 14px;
            }
        """)

        layout = QVBoxLayout(widget)
        layout.addWidget(self.video_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Store widget reference for resize handling
        widget.video_widget = self
        return widget

    def set_video_content(self, video_path_or_content):
        """
        Set video content for playback.
        This method can be extended when actual video playback is implemented.

        Args:
            video_path_or_content: Path to video file or video content
        """
        # For now, just update the label text
        # This will be replaced with actual video playback implementation
        self.video_label.setText(f"Playing: {video_path_or_content}")
        self.video_label.setStyleSheet("""
            QLabel {
                background-color: #222;
                border: 1px solid #666;
                border-radius: 3px;
                color: #fff;
                font-size: 12px;
            }
        """)
