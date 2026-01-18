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
        self.setMinimumSize(450, 450)
        self.setFrameStyle(QFrame.Shape.Box)
        self.selected_electrodes = set()

        # Load head image
        self.head_image = QPixmap("airobo_trainer/assets/images/head.jpeg")
        if self.head_image.isNull():
            # Fallback if image can't be loaded
            self.head_image = None

        # Define electrode positions as percentages relative to image (0.0 to 1.0)
        # 32 electrodes using 10-20 international system
        # Head is oriented upside down (top of image = back of head, bottom = front of head)
        # Adjusted positions: frontal electrodes higher, central/parietal electrodes much higher
        self.relative_electrode_positions = [
            (0.38, 0.83),  # FP1 - left frontopolar (bottom of head, moved slightly higher)
            (0.62, 0.83),  # FP2 - right frontopolar (also at bottom, slightly different position)
            (0.42, 0.74),  # AF3 - left anterior frontal (moved higher)
            (0.58, 0.74),  # AF4 - right anterior frontal (moved higher)
            (0.25, 0.71),  # F7 - left frontal (moved ~7% higher as requested)
            (0.38, 0.65),  # F3 - left frontal (moved much higher)
            (0.50, 0.62),  # FZ - frontal midline (moved much higher)
            (0.62, 0.65),  # F4 - right frontal (moved much higher)
            (0.75, 0.71),  # F8 - right frontal (moved ~7% higher as requested)
            (0.22, 0.58),  # FC5 - left frontocentral (moved higher)
            (0.38, 0.55),  # FC1 - left frontocentral (moved higher)
            (0.62, 0.55),  # FC2 - right frontocentral (moved higher)
            (0.78, 0.58),  # FC6 - right frontocentral (moved higher)
            (0.18, 0.48),  # T7 - left temporal (moved higher)
            (0.32, 0.45),  # C3 - left central (moved higher)
            (0.50, 0.42),  # CZ - central midline (moved higher)
            (0.68, 0.45),  # C4 - right central (moved higher)
            (0.82, 0.48),  # T8 - right temporal (moved higher)
            (0.22, 0.35),  # CP5 - left centroparietal (moved higher)
            (0.38, 0.38),  # CP1 - left centroparietal (moved higher)
            (0.62, 0.38),  # CP2 - right centroparietal (moved higher)
            (0.78, 0.35),  # CP6 - right centroparietal (moved higher)
            (0.18, 0.28),  # P7 - left parietal (moved higher)
            (0.32, 0.32),  # P3 - left parietal (moved higher)
            (0.50, 0.28),  # PZ - parietal midline (moved higher)
            (0.68, 0.32),  # P4 - right parietal (moved higher)
            (0.82, 0.28),  # P8 - right parietal (moved higher)
            (0.25, 0.15),  # PO7 - left parieto-occipital (moved much higher)
            (0.35, 0.20),  # PO3 - left parieto-occipital (moved much higher)
            (0.65, 0.20),  # PO4 - right parieto-occipital (moved much higher)
            (0.75, 0.15),  # PO8 - right parieto-occipital (moved much higher)
            (0.50, 0.10),  # OZ - occipital midline (top of head)
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
            labels = ["FP1", "FP2", "AF3", "AF4", "F7", "F3", "FZ", "F4", "F8", "FC5", "FC1", "FC2", "FC6", "T7", "C3", "CZ", "C4", "T8", "CP5", "CP1", "CP2", "CP6", "P7", "P3", "PZ", "P4", "P8", "PO7", "PO3", "PO4", "PO8", "OZ"]
            if i < len(labels):
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

        # Sampling rate
        self.sampling_rate_combo = QComboBox()
        self.sampling_rate_combo.addItems(["250 Hz", "500 Hz"])
        params_layout.addWidget(QLabel("Sampling Rate:"))
        params_layout.addWidget(self.sampling_rate_combo)

        # Bandpass filter dropdown
        self.bandpass_combo = QComboBox()
        self.bandpass_combo.addItems([
            "0.5Hz-50Hz",
            "1Hz-40Hz",
            "2Hz-30Hz",
            "4Hz-20Hz",
            "8Hz-12Hz",
            "0.1Hz-100Hz",
            "None"
        ])
        params_layout.addWidget(QLabel("Bandpass Filter:"))
        params_layout.addWidget(self.bandpass_combo)

        # Notch filter dropdown
        self.notch_combo = QComboBox()
        self.notch_combo.addItems([
            "None",
            "50Hz",
            "60Hz",
            "50Hz + 60Hz",
            "50Hz (Cascading)",
            "60Hz (Cascading)"
        ])
        params_layout.addWidget(QLabel("Notch Filter:"))
        params_layout.addWidget(self.notch_combo)

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
            "bandpass_filter": self.bandpass_combo.currentText(),
            "notch_filter": self.notch_combo.currentText(),
        }
