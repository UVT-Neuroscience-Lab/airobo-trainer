"""
Leaderboard View - Displays and manages leaderboard functionality
Follows the View component of MVC architecture
"""

from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QLineEdit,
    QDialog,
    QDialogButtonBox,
    QMessageBox,
    QSizePolicy,
)
from PyQt6.QtCore import Qt, pyqtSignal, QEvent
from PyQt6.QtGui import QFont

from airobo_trainer.models.scoring_system import ScoringSystem


class LeaderboardEntryDialog(QDialog):
    """
    Dialog for entering a name when achieving a high score.
    """

    def __init__(self, score: int, parent=None):
        super().__init__(parent)
        self.score = score
        self.player_name = ""
        self._init_ui()

    def _init_ui(self):
        """Set up the dialog interface."""
        self.setWindowTitle("High Score!")
        self.setModal(True)
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)

        # Title
        title_label = QLabel("Congratulations!")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title_label)

        # Score display
        score_label = QLabel(f"You achieved a score of: {self.score}")
        score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        score_label.setStyleSheet("font-size: 16px; margin: 10px;")
        layout.addWidget(score_label)

        # Message
        message_label = QLabel("Enter your name for the leaderboard:")
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message_label.setStyleSheet("font-size: 14px; margin: 10px;")
        layout.addWidget(message_label)

        # Name input
        self.name_input = QLineEdit()
        self.name_input.setMaxLength(20)
        self.name_input.setStyleSheet("""
            QLineEdit {
                font-size: 14px;
                padding: 8px;
                border: 2px solid #ccc;
                border-radius: 5px;
            }
        """)
        layout.addWidget(self.name_input)

        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self._accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        # Set focus to name input
        self.name_input.setFocus()

    def _accept(self):
        """Handle OK button click."""
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Invalid Name", "Please enter a name.")
            return

        self.player_name = name
        self.accept()


class LeaderboardView(QMainWindow):
    """
    View for displaying the leaderboard.
    """

    # Custom signals
    back_requested = pyqtSignal()

    def __init__(self, scoring_system: ScoringSystem = None):
        super().__init__()
        self.scoring_system = scoring_system or ScoringSystem()
        self._init_ui()

    def _init_ui(self):
        """Set up the leaderboard interface."""
        self.setWindowTitle("AiRobo-Trainer - Leaderboard")
        self.setMinimumSize(600, 575)

        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Back button
        back_button = QPushButton("← Back")
        back_button.clicked.connect(self._on_back_button_clicked)
        back_button.setMaximumWidth(100)
        main_layout.addWidget(back_button, alignment=Qt.AlignmentFlag.AlignLeft)

        # Title
        title_label = QLabel("Leaderboard")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; margin: 20px 0;")
        main_layout.addWidget(title_label)

        # Leaderboard list
        self.leaderboard_list = QListWidget()
        self.leaderboard_list.setStyleSheet("""
            QListWidget {
                font-size: 14px;
                border: 2px solid #ccc;
                border-radius: 8px;
                background-color: #f9f9f9;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #ddd;
            }
            QListWidget::item:nth-child(1) {
                background-color: #FFD700;
                font-weight: bold;
            }
            QListWidget::item:nth-child(2) {
                background-color: #C0C0C0;
                font-weight: bold;
            }
            QListWidget::item:nth-child(3) {
                background-color: #CD7F32;
                font-weight: bold;
            }
        """)
        main_layout.addWidget(self.leaderboard_list)

        # Update leaderboard display
        self._update_leaderboard()

    def _update_leaderboard(self):
        """Update the leaderboard display."""
        # Reload leaderboard data from file to ensure we have the latest scores
        self.scoring_system.leaderboard = self.scoring_system._load_leaderboard()

        self.leaderboard_list.clear()
        leaderboard = self.scoring_system.get_leaderboard()

        if not leaderboard:
            item = QListWidgetItem("No scores yet!")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.leaderboard_list.addItem(item)
            return

        for i, entry in enumerate(leaderboard, 1):
            rank_text = f"{i}."
            name_text = entry.name or "Anonymous"
            score_text = f"{entry.score} points"
            date_text = entry.timestamp.strftime("%Y-%m-%d %H:%M")

            display_text = f"{rank_text:<3} {name_text:<20} {score_text:<12} {date_text}"
            item = QListWidgetItem(display_text)
            self.leaderboard_list.addItem(item)

    def _on_back_button_clicked(self):
        """Handle back button click."""
        self.back_requested.emit()

    def showEvent(self, event: QEvent):
        """Handle when the view is shown - refresh leaderboard data."""
        super().showEvent(event)
        self._update_leaderboard()

    @staticmethod
    def show_leaderboard_entry_dialog(score: int, parent=None) -> str:
        """
        Show the leaderboard entry dialog.

        Args:
            score: The score achieved
            parent: Parent widget

        Returns:
            Player name if entered, empty string if cancelled
        """
        dialog = LeaderboardEntryDialog(score, parent)
        result = dialog.exec()

        if result == QDialog.DialogCode.Accepted:
            return dialog.player_name
        return ""
