# AiRobo-Trainer

**Stroke Rehabilitation Trainer powered by Brain-Computer Interface (BCI) Technology**

AiRobo-Trainer is a medical application designed to assist stroke patients in their rehabilitation journey through BCI-enabled training exercises and monitoring. Built with PyQt6 following strict MVC (Model-View-Controller) architecture and Python best practices.

## Overview

This application provides healthcare professionals and researchers with a configurable interface to manage BCI-based rehabilitation training modules for stroke patients. The system allows configuration of different training modalities including:

- **Text Commands**: Text-based command training for cognitive rehabilitation
- **Avatar**: Avatar-controlled movement exercises for motor skill recovery
- **Video**: Video-guided rehabilitation exercises and feedback

## Features

- **BCI Integration Ready**: Designed for integration with Brain-Computer Interface systems
- **Medical-Grade Architecture**: Strict MVC separation ensuring reliability and maintainability
- **Configurable Training Modules**: Easy configuration of rehabilitation training modes
- **PyQt6 UI**: Modern, accessible Qt6 interface optimized for clinical settings
- **Type Hints**: Full type annotations for code safety and reliability
- **Comprehensive Tests**: Unit tests for all components with pytest
- **Best Practices**: Follows PEP 8 and medical software development standards

## Project Structure

```
airobo-trainer/
├── airobo_trainer/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── item_model.py          # Data management
│   ├── views/
│   │   ├── __init__.py
│   │   └── main_view.py           # UI components
│   ├── controllers/
│   │   ├── __init__.py
│   │   └── main_controller.py     # Application logic
│   └── tests/
│       ├── __init__.py
│       ├── test_item_model.py
│       ├── test_main_view.py
│       └── test_main_controller.py
├── main.py                         # Application entry point
├── requirements.txt                # Dependencies
├── pytest.ini                      # Test configuration
├── setup.py                        # Package setup
└── README.md
```

## Architecture

### Model (Data Layer)
The `ItemModel` class manages BCI training configuration data:
- Manages available training modules (Text Commands, Avatar, Video)
- Remove and retrieve training configurations
- Data validation and business rules
- No dependencies on View or Controller

### View (Presentation Layer)
The `MainView` class handles the configuration UI:
- "Configure BCI" interface for training module selection
- List widget displaying available training modules
- Remove and clear controls for configuration management
- Emits signals for user interactions
- No business logic, only UI updates

### Controller (Logic Layer)
The `MainController` class coordinates Model and View:
- Connects UI interactions to data operations
- Manages training module configuration logic
- Updates View based on Model changes
- Ensures data consistency for BCI training sessions

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Setup

1. Clone or download this repository:
```bash
git clone <repository-url>
cd airobo-trainer
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv

# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

Run the application using Python:

```bash
python main.py
```

Or make it executable (Unix-like systems):

```bash
chmod +x main.py
./main.py
```

## Running Tests

The project includes comprehensive unit tests using pytest.

### Run all tests:
```bash
pytest
```

### Run with coverage report:
```bash
pytest --cov=airobo_trainer --cov-report=term-missing
```

### Run specific test file:
```bash
pytest airobo_trainer/tests/test_item_model.py
```

### Run specific test:
```bash
pytest airobo_trainer/tests/test_item_model.py::TestItemModel::test_add_item_success
```

### Run tests with verbose output:
```bash
pytest -v
```

## Development

### Code Quality Tools

Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

#### Format code with Black:
```bash
black airobo_trainer/
```

#### Check code style with flake8:
```bash
flake8 airobo_trainer/
```

#### Type checking with mypy:
```bash
mypy airobo_trainer/
```

#### Linting with pylint:
```bash
pylint airobo_trainer/
```

## Usage

The application provides a BCI training configuration interface:

### Configure BCI Training Modules

The system comes pre-configured with three rehabilitation training modules:
- **Text Commands**: For cognitive rehabilitation and text-based command training
- **Avatar**: For motor skill recovery through avatar-controlled exercises
- **Video**: For video-guided rehabilitation exercises with visual feedback

### Managing Training Modules

1. **Remove Selected**: Select a training module from the list and click "Remove Selected" to exclude it from the current session
2. **Clear All**: Click "Clear All" to remove all training modules and start fresh

This configuration interface allows healthcare professionals to customize the training session based on the patient's rehabilitation needs and progress.

## Extending the Application

### Adding New Training Modules

To add new rehabilitation training modules to the system:

1. **Update Model**: Modify `airobo_trainer/models/item_model.py` to include new training module names
2. **Extend View**: Add UI components in `airobo_trainer/views/` for module-specific controls
3. **Update Controller**: Implement logic in `airobo_trainer/controllers/` to handle new module interactions

### Integrating BCI Hardware

To integrate actual BCI hardware:

1. Create a new BCI interface module in `airobo_trainer/models/`
2. Implement signal processing and data acquisition logic
3. Connect BCI signals to training module controllers
4. Add real-time feedback mechanisms in the View layer

### Custom Rehabilitation Protocols

Healthcare professionals can extend the system by:

1. Adding protocol-specific models for patient data
2. Creating custom views for protocol monitoring
3. Implementing protocol-specific controllers for data flow management

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Medical Disclaimer

This software is provided for research and educational purposes. It is not intended as a medical device and should not be used for clinical diagnosis or treatment without proper validation and regulatory approval. Always consult qualified healthcare professionals for medical advice.

## Acknowledgments

- Built with [PyQt6](https://www.riverbankcomputing.com/software/pyqt/)
- Testing with [pytest](https://pytest.org/) and [pytest-qt](https://pytest-qt.readthedocs.io/)
- Developed for stroke rehabilitation research and BCI technology advancement
