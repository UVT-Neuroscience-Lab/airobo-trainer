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
    QComboBox,
    QGroupBox,
    QFrame,
    QLineEdit,
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
            labels = [
                "FP1",
                "FP2",
                "AF3",
                "AF4",
                "F7",
                "F3",
                "FZ",
                "F4",
                "F8",
                "FC5",
                "FC1",
                "FC2",
                "FC6",
                "T7",
                "C3",
                "CZ",
                "C4",
                "T8",
                "CP5",
                "CP1",
                "CP2",
                "CP6",
                "P7",
                "P3",
                "PZ",
                "P4",
                "P8",
                "PO7",
                "PO3",
                "PO4",
                "PO8",
                "OZ",
            ]
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
        self._set_default_electrodes()

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

        # Output Configuration section
        output_group = QGroupBox("Output Configuration")
        output_layout = QVBoxLayout(output_group)

        # Output folder path
        self.output_path_edit = QLineEdit("airobo_trainer/output")
        output_layout.addWidget(QLabel("Output Folder Path:"))
        output_layout.addWidget(self.output_path_edit)

        main_layout.addWidget(output_group)

        # BCI Parameters section
        params_group = QGroupBox("BCI Parameters")
        params_layout = QVBoxLayout(params_group)

        # Sampling rate
        self.sampling_rate_combo = QComboBox()
        self.sampling_rate_combo.addItems(["250 Hz", "500 Hz"])
        self.sampling_rate_combo.setCurrentText("500 Hz")  # Default to 500 Hz
        self.sampling_rate_combo.currentTextChanged.connect(self._on_sampling_rate_changed)
        params_layout.addWidget(QLabel("Sampling Rate:"))
        params_layout.addWidget(self.sampling_rate_combo)

        # Bandpass filter dropdown
        self.bandpass_combo = QComboBox()
        params_layout.addWidget(QLabel("Bandpass Filter:"))
        params_layout.addWidget(self.bandpass_combo)

        # Notch filter dropdown
        self.notch_combo = QComboBox()
        params_layout.addWidget(QLabel("Notch Filter:"))
        params_layout.addWidget(self.notch_combo)

        main_layout.addWidget(params_group)

        # Initialize filter options based on default sampling rate
        self._update_filter_options()

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

    def _on_sampling_rate_changed(self):
        """Handle sampling rate change."""
        self._update_filter_options()

    def _update_filter_options(self):
        """Update filter options based on selected sampling rate."""
        sampling_rate = self.sampling_rate_combo.currentText()

        # Based on the actual device filters queried, these are the available options
        if sampling_rate == "250 Hz":
            bandpass_filters = [
                "0.1 – 30 Hz Bandpass",
                "0.1 – 60 Hz Bandpass",
                "0.5 – 30 Hz Bandpass",
                "0.5 – 60 Hz Bandpass",
                "2.0 – 30 Hz Bandpass",
                "2.0 – 60 Hz Bandpass",
                "5.0 – 30 Hz Bandpass",
                "5.0 – 60 Hz Bandpass",
                "0.1 Hz Highpass",
                "1.0 Hz Highpass",
                "2.0 Hz Highpass",
                "5.0 Hz Highpass",
                "30 Hz Lowpass",
                "60 Hz Lowpass",
                "100 Hz Lowpass",
                "None - No filter applied",
            ]
        else:  # 500 Hz
            bandpass_filters = [
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

        # Update bandpass filter options
        current_bandpass = self.bandpass_combo.currentText()
        self.bandpass_combo.clear()
        self.bandpass_combo.addItems(bandpass_filters)

        # Try to restore previous selection if it's still valid
        if current_bandpass in bandpass_filters:
            self.bandpass_combo.setCurrentText(current_bandpass)
        else:
            # Default to "0.1 – 60 Hz Bandpass" (user preference)
            default_option = "0.1 – 60 Hz Bandpass"
            if default_option in bandpass_filters:
                self.bandpass_combo.setCurrentText(default_option)
            else:
                self.bandpass_combo.setCurrentIndex(0)

        # Notch filters are the same for both sampling rates
        notch_filters = ["None", "50Hz", "60Hz"]
        current_notch = self.notch_combo.currentText()
        self.notch_combo.clear()
        self.notch_combo.addItems(notch_filters)

        # Restore notch filter selection if valid
        if current_notch in notch_filters:
            self.notch_combo.setCurrentText(current_notch)
        else:
            # Default to "50Hz" (user preference)
            self.notch_combo.setCurrentText("50Hz")

    def get_selected_electrodes(self):
        """Get the set of selected electrode indices."""
        return self.electrode_widget.selected_electrodes.copy()

    def get_bci_parameters(self):
        """Get current BCI parameter settings."""
        return {
            "output_path": self.output_path_edit.text(),
            "sampling_rate": self.sampling_rate_combo.currentText(),
            "bandpass_filter": self.bandpass_combo.currentText(),
            "notch_filter": self.notch_combo.currentText(),
        }

    def _set_default_electrodes(self):
        """Set default electrodes for left/right arm movement detection."""
        # Default electrodes for motor imagery (left/right hand movement):
        # C3 (left motor cortex), CZ (central), C4 (right motor cortex)
        # Indices: C3=14, CZ=15, C4=16
        default_electrodes = {14, 15, 16}  # C3, CZ, C4
        self.electrode_widget.selected_electrodes = default_electrodes.copy()
        self.electrode_widget.update()
        self._on_electrode_selected(0)  # Update status label

    def set_status(self, message: str):
        """Set the status label text."""
        self.status_label.setText(message)
