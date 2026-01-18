"""
Main View - UI Layout and Components
Follows the View component of MVC architecture
"""

from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QListWidget,
    QPushButton,
    QLabel,
    QMessageBox,
)
from PyQt6.QtCore import Qt, pyqtSignal


class MainView(QMainWindow):
    """
    Main application window view.

    This class handles all UI components and layout. It emits signals
    for user interactions but does not contain business logic.
    """

    # Custom signals for user interactions
    remove_item_requested = pyqtSignal(int)
    clear_all_requested = pyqtSignal()

    def __init__(self) -> None:
        """Initialize the main view with all UI components."""
        super().__init__()
        self._init_ui()

    def _init_ui(self) -> None:
        """Set up the user interface."""
        self.setWindowTitle("AiRobo-Trainer - MVC Boilerplate")
        self.setMinimumSize(600, 400)

        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Title label
        title_label = QLabel("Configure BCI")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        main_layout.addWidget(title_label)

        # Remove button at the top (full width)
        self.remove_button = QPushButton("Remove Selected")
        self.remove_button.clicked.connect(self._on_remove_button_clicked)
        main_layout.addWidget(self.remove_button)

        # List widget to display items
        self.list_widget = QListWidget()
        self.list_widget.setAlternatingRowColors(True)
        main_layout.addWidget(self.list_widget)

        # Clear All button at the bottom
        self.clear_button = QPushButton("Clear All")
        self.clear_button.clicked.connect(self._on_clear_button_clicked)
        main_layout.addWidget(self.clear_button)

        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: gray; margin: 5px;")
        main_layout.addWidget(self.status_label)

    def _on_remove_button_clicked(self) -> None:
        """Handle remove button click event."""
        current_row = self.list_widget.currentRow()
        if current_row >= 0:
            self.remove_item_requested.emit(current_row)
        else:
            self.show_warning("No Selection", "Please select an item to remove.")

    def _on_clear_button_clicked(self) -> None:
        """Handle clear button click event."""
        if self.list_widget.count() > 0:
            self.clear_all_requested.emit()

    def update_list(self, items: list[str]) -> None:
        """
        Update the list widget with new items.

        Args:
            items: List of items to display
        """
        self.list_widget.clear()
        self.list_widget.addItems(items)

    def set_status(self, message: str) -> None:
        """
        Update the status label with a message.

        Args:
            message: The status message to display
        """
        self.status_label.setText(message)

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
