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
from PyQt6.QtCore import Qt, pyqtSignal, QRect, QTimer, QUrl
from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QPixmap
from PyQt6.QtMultimedia import QMediaPlayer
from PyQt6.QtMultimediaWidgets import QVideoWidget


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

            # Only color activated segments, others remain grey
            if activation > 10:  # Threshold for considering it "activated"
                # Color based on segment position: red, orange, yellow, yellowish-green, light green, dark green
                if i == 0:
                    color = QColor(255, 0, 0)  # Red (bottom segment)
                elif i == 1:
                    color = QColor(255, 165, 0)  # Orange
                elif i == 2:
                    color = QColor(255, 255, 0)  # Yellow
                elif i == 3:
                    color = QColor(173, 255, 47)  # Yellowish-green
                elif i == 4:
                    color = QColor(144, 238, 144)  # Light green
                else:  # i == 5
                    color = QColor(0, 100, 0)  # Dark green (top segment)

                # Apply activation level as opacity
                if activation < 30:
                    # Very low activation - make it more transparent
                    color.setAlpha(100)
                elif activation < 70:
                    # Medium activation - semi-transparent
                    color.setAlpha(180)
                else:
                    # High activation - fully opaque
                    color.setAlpha(255)
            else:
                # Not activated - use grey
                color = QColor(128, 128, 128)  # Grey for inactive segments

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
        self.current_mode = "relax"  # "left", "right", or "relax"
        self.oscillation_timer = QTimer()
        self.oscillation_timer.timeout.connect(self._update_muscle_bars)
        self.transition_timer = QTimer()
        self.transition_timer.timeout.connect(self._update_transition)
        self.transition_progress = 0.0  # 0.0 to 1.0
        self.transition_duration = 2000  # 2 seconds in milliseconds
        self.transitioning = False
        self.current_left_levels = [0] * 6
        self.current_right_levels = [0] * 6
        self.target_left_levels = [0] * 6
        self.target_right_levels = [0] * 6
        self._init_ui()
        # Start with relax oscillation
        self._start_gradual_transition("relax")

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

        # Add status label for compatibility with controller
        self.status_label = QLabel("")
        self.status_label.hide()  # Hide by default since experiments don't show status

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

    def keyPressEvent(self, event):
        """Handle keyboard shortcuts for simulation."""
        if event.key() == Qt.Key.Key_1:  # Left hand
            self.set_simulation_mode("left")
        elif event.key() == Qt.Key.Key_2:  # Right hand
            self.set_simulation_mode("right")
        elif event.key() == Qt.Key.Key_3:  # Relax
            self.set_simulation_mode("relax")
        else:
            super().keyPressEvent(event)

    def set_simulation_mode(self, mode: str):
        """Set the simulation mode and update content accordingly."""
        # Update content immediately
        self.current_mode = mode

        if mode == "left":
            self._show_left_hand_content()
        elif mode == "right":
            self._show_right_hand_content()
        elif mode == "relax":
            self._show_relax_content()

        # Start gradual transition to new oscillation pattern
        self._start_gradual_transition(mode)

    def _start_gradual_transition(self, target_mode: str):
        """Start a gradual transition to the target oscillation pattern."""
        # Stop any existing transitions
        self.transition_timer.stop()
        self.oscillation_timer.stop()

        # Set current levels as starting point
        self.current_left_levels = [self.left_arm_bar.activation_levels[i] for i in range(6)]
        self.current_right_levels = [self.right_arm_bar.activation_levels[i] for i in range(6)]

        # Calculate target levels based on mode
        if target_mode == "left":
            # Left hand active: 53-87%, Right hand inactive: 6-18%
            left_activation = 70  # Average target
            right_activation = 12  # Average target
        elif target_mode == "right":
            # Right hand active: 53-87%, Left hand inactive: 6-18%
            right_activation = 70  # Average target
            left_activation = 12  # Average target
        elif target_mode == "relax":
            # Both arms oscillating: 12-34%
            left_activation = 23  # Average target
            right_activation = 23  # Average target
        else:
            return

        # Calculate target levels for each bar segment
        self.target_left_levels = []
        self.target_right_levels = []
        for i in range(6):
            left_level = min(100, max(0, int((left_activation - i * 16.7) * 6)))
            right_level = min(100, max(0, int((right_activation - i * 16.7) * 6)))
            self.target_left_levels.append(left_level)
            self.target_right_levels.append(right_level)

        # Start the gradual transition
        self.transition_progress = 0.0
        self.transitioning = True
        self.transition_timer.start(50)  # Update every 50ms for smooth transition

    def _update_transition(self):
        """Update the gradual transition between oscillation patterns."""
        if not self.transitioning:
            return

        # Update progress (2 seconds total = 2000ms, updates every 50ms = 40 steps)
        self.transition_progress += 0.025  # 1/40 = 0.025

        if self.transition_progress >= 1.0:
            # Transition complete
            self.transition_progress = 1.0
            self.transitioning = False
            self.transition_timer.stop()
            # Start normal oscillation
            self.oscillation_timer.start(200)
        else:
            # Interpolate between current and target levels
            for i in range(6):
                current_left = self.current_left_levels[i]
                target_left = self.target_left_levels[i]
                current_right = self.current_right_levels[i]
                target_right = self.target_right_levels[i]

                # Smooth interpolation
                interpolated_left = (
                    current_left + (target_left - current_left) * self.transition_progress
                )
                interpolated_right = (
                    current_right + (target_right - current_right) * self.transition_progress
                )

                self.left_arm_bar.set_activation(i, int(interpolated_left))
                self.right_arm_bar.set_activation(i, int(interpolated_right))

    def _show_left_hand_content(self):
        """Show content for left hand simulation."""
        # This will be overridden by subclasses
        pass

    def _show_right_hand_content(self):
        """Show content for right hand simulation."""
        # This will be overridden by subclasses
        pass

    def _show_relax_content(self):
        """Show content for relax period."""
        # This will be overridden by subclasses
        pass

    def _update_muscle_bars(self):
        """Update muscle bar activations with oscillating values."""
        import random

        if self.current_mode == "left":
            # Left hand active: 53-87%, Right hand inactive: 6-18%
            left_activation = random.randint(53, 87)
            right_activation = random.randint(6, 18)
        elif self.current_mode == "right":
            # Right hand active: 53-87%, Left hand inactive: 6-18%
            right_activation = random.randint(53, 87)
            left_activation = random.randint(6, 18)
        elif self.current_mode == "relax":
            # Both arms oscillating: 12-34%
            left_activation = random.randint(12, 34)
            right_activation = random.randint(12, 34)
        else:
            return

        # Fill bars from bottom to top based on activation level
        # Each bar represents ~16.7% of total activation
        for i in range(6):
            left_level = min(100, max(0, int((left_activation - i * 16.7) * 6)))
            right_level = min(100, max(0, int((right_activation - i * 16.7) * 6)))

            self.left_arm_bar.set_activation(i, left_level)
            self.right_arm_bar.set_activation(i, right_level)

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

    def set_status(self, message: str):
        """Set the status label text (hidden by default for experiments)."""
        self.status_label.setText(message)


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
        self.text_label = QLabel(
            "Command: RELAX\n\nPlease follow the instructions to control the system using your thoughts."
        )
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text_label.setWordWrap(True)  # Enable word wrapping
        self.text_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #333;
                line-height: 1.4;
            }
        """)
        layout.addWidget(self.text_label, alignment=Qt.AlignmentFlag.AlignCenter)

        return widget

    def _show_left_hand_content(self):
        """Show left hand command."""
        self.text_label.setText(
            "LEFT HAND\n\nImagine moving your left hand.\nFocus on the movement and muscle activation."
        )

    def _show_right_hand_content(self):
        """Show right hand command."""
        self.text_label.setText(
            "RIGHT HAND\n\nImagine moving your right hand.\nFocus on the movement and muscle activation."
        )

    def _show_relax_content(self):
        """Show relax command."""
        self.text_label.setText(
            "Command: RELAX\n\nPlease follow the instructions to control the system using your thoughts."
        )


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

        layout = QVBoxLayout(widget)

        # Avatar image label that will be resized dynamically
        self.avatar_label = QLabel()
        self.avatar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.avatar_label.setSizePolicy(
            QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored
        )  # Fixed size
        self.avatar_label.setFixedSize(400, 500)  # Fixed size to prevent collapse

        # Bottom text label for arm indication
        self.arm_label = QLabel("Left Arm")
        self.arm_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.arm_label.setStyleSheet("""
            QLabel {
                background-color: #add8e6;
                color: #000;
                font-size: 16px;
                font-weight: bold;
                padding: 12px;
                border-radius: 5px;
                margin: 5px;
            }
        """)
        self.arm_label.setMaximumHeight(60)

        # Start in relax mode - no initial image
        self.arm_label.setText("Relax")

        layout.addWidget(self.avatar_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.arm_label, alignment=Qt.AlignmentFlag.AlignBottom)

        # Store widget reference for resize handling
        widget.avatar_widget = self
        return widget

    def _load_avatar_image(self, hand: str):
        """Load the appropriate avatar image for the specified hand."""
        if hand == "left":
            image_path = "airobo_trainer/assets/images/l_hand.png"
        elif hand == "right":
            image_path = "airobo_trainer/assets/images/r_hand.png"
        else:
            image_path = "airobo_trainer/assets/images/l_hand.png"  # Default

        self.original_pixmap = QPixmap(image_path)
        if not self.original_pixmap.isNull():
            # Immediately scale to fit available space
            self._scale_avatar_image()
        else:
            # Fallback if image can't be loaded
            self.avatar_label.setText(f"Avatar Image\n(Could not load {image_path})")
            self.avatar_label.setStyleSheet("font-size: 14px; color: #666;")

    def _show_left_hand_content(self):
        """Show left hand avatar."""
        self._load_avatar_image("left")
        self.arm_label.setText("Left Arm")

    def _show_right_hand_content(self):
        """Show right hand avatar."""
        self._load_avatar_image("right")
        self.arm_label.setText("Right Arm")

    def _show_relax_content(self):
        """Show relax state - clear avatar image and update label."""
        self.avatar_label.clear()  # Clear the image
        self.arm_label.setText("Relax")

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

    def __init__(self, experiment_name: str):
        # Preload videos for seamless switching
        self._preload_videos()
        super().__init__(experiment_name)

    def _preload_videos(self):
        """Preload video files for seamless playback switching."""
        # For now, just check if files exist and store paths
        # In a real implementation, this would load video data into memory
        import os

        self.left_video_path = "airobo_trainer/assets/videos/l_hand.mp4"
        self.right_video_path = "airobo_trainer/assets/videos/r_hand.mp4"

        # Check if video files exist
        self.left_video_exists = os.path.exists(self.left_video_path)
        self.right_video_exists = os.path.exists(self.right_video_path)

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

        layout = QVBoxLayout(widget)

        # Create video player and widget
        self.video_player = QMediaPlayer()
        self.video_widget = QVideoWidget()
        self.video_player.setVideoOutput(self.video_widget)
        self.video_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.video_widget.setMinimumSize(400, 500)  # Ensure minimum size
        self.video_widget.show()  # Ensure the widget is visible
        self.video_widget.repaint()  # Force repaint

        # Set up video player for looping and debugging
        self.video_player.mediaStatusChanged.connect(self._on_media_status_changed)
        self.video_player.errorOccurred.connect(self._on_video_error)
        self.video_player.playbackStateChanged.connect(self._on_playback_state_changed)

        # Bottom text label for arm indication
        self.arm_label = QLabel("Left Arm")
        self.arm_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.arm_label.setStyleSheet("""
            QLabel {
                background-color: #add8e6;
                color: #000;
                font-size: 16px;
                font-weight: bold;
                padding: 12px;
                border-radius: 5px;
                margin: 5px;
            }
        """)
        self.arm_label.setMaximumHeight(60)

        layout.addWidget(self.video_widget, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.arm_label, alignment=Qt.AlignmentFlag.AlignBottom)

        # Store widget reference for resize handling
        widget.video_widget = self
        return widget

    def _show_left_hand_content(self):
        """Show left hand video."""
        if self.left_video_exists:
            self.video_player.setSource(QUrl.fromLocalFile(self.left_video_path))
            self.video_widget.update()  # Force refresh
            self.video_player.play()
        self.arm_label.setText("Left Arm")

    def _show_right_hand_content(self):
        """Show right hand video."""
        if self.right_video_exists:
            self.video_player.setSource(QUrl.fromLocalFile(self.right_video_path))
            self.video_widget.update()  # Force refresh
            self.video_player.play()
        self.arm_label.setText("Right Arm")

    def _show_relax_content(self):
        """Show relax state."""
        self.video_player.stop()
        self.arm_label.setText("Relax")

    def _on_media_status_changed(self, status):
        """Handle media status changes for looping videos."""
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            # Loop the video
            self.video_player.setPosition(0)
            self.video_player.play()

    def _on_video_error(self, error, error_string):
        """Handle video playback errors."""
        print(f"Video error: {error} - {error_string}")
        # Could show an error message to the user here

    def _on_playback_state_changed(self, state):
        """Handle playback state changes - no debug output."""
        pass  # Removed debug output as requested

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
