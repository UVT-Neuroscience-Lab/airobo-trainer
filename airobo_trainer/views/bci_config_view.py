"""
BCI Configuration View - BCI Headset Configuration Interface
Follows the View component of MVC architecture
"""

from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QCheckBox,
    QSpinBox,
    QComboBox,
    QGroupBox,
    QFrame,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPainter, QBrush, QColor, QPen, QPixmap


class ElectrodeWidget(QFrame):
    """
    Custom widget for electrode selection visualization.
    Shows a head-shaped area with selectable electrode positions.
    """

    electrode_selected = pyqtSignal(int)  # Signal emitted when electrode is clicked

    def __init__(self):
        super().__init__()
        self.setMinimumSize(300, 300)
        self.setFrameStyle(QFrame.Shape.Box)
        self.selected_electrodes = set()

        # Load head image
        self.head_image = QPixmap("airobo_trainer/assets/images/head.jpeg")
        if self.head_image.isNull():
            # Fallback if image can't be loaded
            self.head_image = None

        # Define electrode positions as percentages relative to image (0.0 to 1.0)
        # These represent positions on the head image
        self.relative_electrode_positions = [
            (0.50, 0.15),  # Fz - frontal midline
            (0.33, 0.25),  # F3 - left frontal
            (0.67, 0.25),  # F4 - right frontal
            (0.25, 0.40),  # C3 - left central
            (0.50, 0.40),  # Cz - central midline
            (0.75, 0.40),  # C4 - right central
            (0.33, 0.60),  # P3 - left parietal
            (0.67, 0.60),  # P4 - right parietal
            (0.50, 0.75),  # Oz - occipital midline
        ]

    def _get_image_geometry(self):
        """Get the current image geometry (position and size within widget)."""
        if self.head_image and not self.head_image.isNull():
            # Scale image to fit widget while maintaining aspect ratio
            scaled_image = self.head_image.scaled(
                self.width(),
                self.height(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            # Center the image
            x_offset = (self.width() - scaled_image.width()) // 2
            y_offset = (self.height() - scaled_image.height()) // 2
            return x_offset, y_offset, scaled_image.width(), scaled_image.height()
        else:
            # Fallback geometry for circle
            return 50, 30, 200, 240

    def _get_absolute_electrode_positions(self):
        """Calculate absolute electrode positions based on current image geometry."""
        x_offset, y_offset, img_width, img_height = self._get_image_geometry()

        absolute_positions = []
        for rel_x, rel_y in self.relative_electrode_positions:
            abs_x = x_offset + int(rel_x * img_width)
            abs_y = y_offset + int(rel_y * img_height)
            absolute_positions.append((abs_x, abs_y))

        return absolute_positions

    def paintEvent(self, event):
        """Paint the electrode visualization."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw head image as background
        if self.head_image and not self.head_image.isNull():
            x_offset, y_offset, img_width, img_height = self._get_image_geometry()
            # Scale image to fit widget while maintaining aspect ratio
            scaled_image = self.head_image.scaled(
                self.width(),
                self.height(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            painter.drawPixmap(x_offset, y_offset, scaled_image)
        else:
            # Fallback: Draw head outline if image can't be loaded
            painter.setPen(QPen(Qt.GlobalColor.black, 2))
            painter.setBrush(QBrush(QColor(240, 240, 240)))
            painter.drawEllipse(50, 30, 200, 240)

        # Get current absolute electrode positions
        electrode_positions = self._get_absolute_electrode_positions()

        # Draw electrodes
        for i, (x, y) in enumerate(electrode_positions):
            if i in self.selected_electrodes:
                painter.setBrush(QBrush(QColor(0, 255, 0)))  # Green for selected
            else:
                painter.setBrush(QBrush(QColor(255, 0, 0)))  # Red for unselected

            painter.drawEllipse(x - 10, y - 10, 20, 20)

            # Draw electrode label
            painter.setPen(QPen(Qt.GlobalColor.white, 1))
            painter.setBrush(QBrush(Qt.BrushStyle.NoBrush))
            labels = ["Fz", "F3", "F4", "C3", "Cz", "C4", "P3", "P4", "Oz"]
            painter.drawText(x - 10, y + 25, labels[i])

    def mousePressEvent(self, event):
        """Handle mouse clicks on electrodes."""
        electrode_positions = self._get_absolute_electrode_positions()
        for i, (x, y) in enumerate(electrode_positions):
            if (
                x - 10 <= event.position().x() <= x + 10
                and y - 10 <= event.position().y() <= y + 10
            ):
                if i in self.selected_electrodes:
                    self.selected_electrodes.remove(i)
                else:
                    self.selected_electrodes.add(i)
                self.electrode_selected.emit(i)
                self.update()
                break


class BCIConfigView(QMainWindow):
    """
    BCI Configuration View - Interface for configuring BCI headset parameters.

    This class handles the BCI configuration UI including parameter settings
    and electrode selection.
    """

    # Custom signals
    back_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._init_ui()

    def _init_ui(self):
        """Set up the BCI configuration interface."""
        self.setWindowTitle("BCI Configuration")
        self.setMinimumSize(600, 500)

        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Back button at the top
        back_button = QPushButton("← Back")
        back_button.clicked.connect(self._on_back_button_clicked)
        main_layout.addWidget(back_button)

        # BCI Parameters section
        params_group = QGroupBox("BCI Parameters")
        params_layout = QVBoxLayout(params_group)

        # Placeholder parameters
        self.sampling_rate_combo = QComboBox()
        self.sampling_rate_combo.addItems(["250 Hz", "500 Hz", "1000 Hz"])
        params_layout.addWidget(QLabel("Sampling Rate:"))
        params_layout.addWidget(self.sampling_rate_combo)

        self.filter_check = QCheckBox("Enable Bandpass Filter")
        self.filter_check.setChecked(True)
        params_layout.addWidget(self.filter_check)

        self.gain_spin = QSpinBox()
        self.gain_spin.setRange(1, 100)
        self.gain_spin.setValue(24)
        params_layout.addWidget(QLabel("Gain:"))
        params_layout.addWidget(self.gain_spin)

        main_layout.addWidget(params_group)

        # Electrode Selection section
        electrode_group = QGroupBox("Electrode Selection")
        electrode_layout = QVBoxLayout(electrode_group)

        electrode_layout.addWidget(QLabel("Click on electrodes to select/deselect them:"))
        self.electrode_widget = ElectrodeWidget()
        self.electrode_widget.electrode_selected.connect(self._on_electrode_selected)
        electrode_layout.addWidget(self.electrode_widget)

        main_layout.addWidget(electrode_group)

        # Status label
        self.status_label = QLabel("BCI Configuration Ready")
        self.status_label.setStyleSheet("color: gray; margin: 5px;")
        main_layout.addWidget(self.status_label)

    def _on_back_button_clicked(self):
        """Handle back button click."""
        self.back_requested.emit()

    def _on_electrode_selected(self, electrode_index: int):
        """Handle electrode selection change."""
        selected_count = len(self.electrode_widget.selected_electrodes)
        self.status_label.setText(f"Selected {selected_count} electrodes")

    def get_selected_electrodes(self):
        """Get the set of selected electrode indices."""
        return self.electrode_widget.selected_electrodes.copy()

    def get_bci_parameters(self):
        """Get current BCI parameter settings."""
        return {
            "sampling_rate": self.sampling_rate_combo.currentText(),
            "filter_enabled": self.filter_check.isChecked(),
            "gain": self.gain_spin.value(),
        }
