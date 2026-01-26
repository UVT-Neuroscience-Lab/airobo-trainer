"""
Main View - UI Layout and Components
Follows the View component of MVC architecture
"""

from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QListWidget,
    QLabel,
    QMessageBox,
    QPushButton,
)
from PyQt6.QtCore import Qt, pyqtSignal


class MainView(QMainWindow):
    """
    Main application window view.

    This class handles all UI components and layout. It emits signals
    for user interactions but does not contain business logic.
    """

    # Custom signals for user interactions
    configure_bci_requested = pyqtSignal()
    configure_experiment_requested = pyqtSignal()
    leaderboard_requested = pyqtSignal()
    experiment_selected = pyqtSignal(str)

    def __init__(self) -> None:
        """Initialize the main view with all UI components."""
        super().__init__()
        self._init_ui()

    def _init_ui(self) -> None:
        """Set up the user interface."""
        self.setWindowTitle("AiRobo-Trainer")
        self.setMinimumSize(600, 400)

        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Title label
        title_label = QLabel("Mode")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        main_layout.addWidget(title_label)

        # Create a container for the list widget to center it
        list_container = QWidget()
        list_layout = QVBoxLayout(list_container)
        list_layout.setContentsMargins(0, 0, 0, 0)

        # List widget to display items
        self.list_widget = QListWidget()
        self.list_widget.setAlternatingRowColors(True)
        self.list_widget.setMaximumWidth(400)  # Limit width to fit content better
        self.list_widget.itemClicked.connect(self._on_item_clicked)
        list_layout.addWidget(self.list_widget, alignment=Qt.AlignmentFlag.AlignCenter)

        # Center the list container in the main layout
        main_layout.addWidget(list_container, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.setAlignment(list_container, Qt.AlignmentFlag.AlignCenter)

        # Configure BCI button
        self.configure_bci_button = QPushButton("Configure BCI")
        self.configure_bci_button.clicked.connect(self._on_configure_bci_button_clicked)
        main_layout.addWidget(self.configure_bci_button, alignment=Qt.AlignmentFlag.AlignCenter)

        # Configure Experiment button
        self.configure_experiment_button = QPushButton("Configure Experiment")
        self.configure_experiment_button.clicked.connect(
            self._on_configure_experiment_button_clicked
        )
        main_layout.addWidget(
            self.configure_experiment_button, alignment=Qt.AlignmentFlag.AlignCenter
        )

        # Leaderboard button
        self.leaderboard_button = QPushButton("Leaderboard")
        self.leaderboard_button.clicked.connect(self._on_leaderboard_button_clicked)
        main_layout.addWidget(self.leaderboard_button, alignment=Qt.AlignmentFlag.AlignCenter)

    def _on_configure_bci_button_clicked(self) -> None:
        """Handle configure BCI button click event."""
        self.configure_bci_requested.emit()

    def _on_configure_experiment_button_clicked(self) -> None:
        """Handle configure experiment button click event."""
        self.configure_experiment_requested.emit()

    def _on_leaderboard_button_clicked(self) -> None:
        """Handle leaderboard button click event."""
        self.leaderboard_requested.emit()

    def _on_item_clicked(self, item) -> None:
        """Handle item click event."""
        experiment_name = item.text()
        self.experiment_selected.emit(experiment_name)

    def update_list(self, items: list[str]) -> None:
        """
        Update the list widget with new items.

        Args:
            items: List of items to display
        """
        self.list_widget.clear()
        self.list_widget.addItems(items)

    def show_info(self, title: str, message: str) -> None:
        """
        Show an information dialog.

        Args:
            title: Dialog title
            message: Dialog message
        """
        QMessageBox.information(self, title, message)

    def show_warning(self, title: str, message: str) -> None:
        """
        Show a warning dialog.

        Args:
            title: Dialog title
            message: Dialog message
        """
        QMessageBox.warning(self, title, message)

    def show_error(self, title: str, message: str) -> None:
        """
        Show an error dialog.

        Args:
            title: Dialog title
            message: Dialog message
        """
        QMessageBox.critical(self, title, message)

    def get_selected_index(self) -> int:
        """
        Get the currently selected item index.

        Returns:
            The selected index, or -1 if nothing is selected
        """
        return self.list_widget.currentRow()
