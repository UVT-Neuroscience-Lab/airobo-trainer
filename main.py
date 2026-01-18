#!/usr/bin/env python3
"""
AiRobo-Trainer - Main Entry Point

This is the main entry point for the AiRobo-Trainer application.
It initializes the Qt application and the MVC components.
"""

import sys
from PyQt6.QtWidgets import QApplication

from airobo_trainer.controllers.main_controller import MainController


def main() -> int:
    """
    Main application entry point.

    Returns:
        Application exit code
    """
    # Create Qt application instance
    app = QApplication(sys.argv)

    # Set application metadata
    app.setApplicationName("AiRobo-Trainer")
    app.setOrganizationName("AiRobo")
    app.setApplicationVersion("0.1.0")

    # Initialize MVC components through the controller
    controller = MainController()

    # Show the main window
    controller.show()

    # Start the event loop
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
