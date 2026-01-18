#!/usr/bin/env python3
"""
AiRobo-Trainer - Stroke Rehabilitation Trainer powered by BCI

Main Entry Point

This is the main entry point for the AiRobo-Trainer application.
A medical application designed to assist stroke patients in their rehabilitation
journey through BCI-enabled training exercises and monitoring.

It initializes the Qt application and the MVC components.
"""

import sys
from PyQt6.QtWidgets import QApplication

from airobo_trainer.controllers.main_controller import MainController


def main() -> int:
    """
    Main application entry point for BCI Rehabilitation Trainer.

    Returns:
        Application exit code
    """
    # Create Qt application instance
    app = QApplication(sys.argv)

    # Set application metadata
    app.setApplicationName("AiRobo-Trainer - BCI Rehabilitation")
    app.setOrganizationName("AiRobo Medical Systems")
    app.setApplicationVersion("0.1.0")

    # Initialize MVC components through the controller
    controller = MainController()

    # Show the main window
    controller.show()

    # Start the event loop
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
