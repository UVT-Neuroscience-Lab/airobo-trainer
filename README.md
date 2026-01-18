# AiRobo-Trainer

A PyQt6 boilerplate application following strict MVC (Model-View-Controller) architecture and Python best practices.

## Features

- **Strict MVC Architecture**: Clean separation between Model (data), View (UI), and Controller (logic)
- **PyQt6 UI**: Modern Qt6 interface with code-based layouts
- **Type Hints**: Full type annotations for better code quality
- **Comprehensive Tests**: Unit tests for all components with pytest
- **Best Practices**: Follows PEP 8 and Python best practices

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
The `ItemModel` class manages application data:
- Add, remove, and retrieve items
- Data validation and business rules
- No dependencies on View or Controller

### View (Presentation Layer)
The `MainView` class handles UI:
- QMainWindow with list widget, text input, and buttons
- Emits signals for user interactions
- No business logic, only UI updates

### Controller (Logic Layer)
The `MainController` class coordinates Model and View:
- Connects View signals to Model operations
- Handles business logic
- Updates View based on Model changes

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

The application provides a simple item manager interface:

1. **Add Item**: Enter text in the input field and click "Add Item" or press Enter
2. **Remove Item**: Select an item from the list and click "Remove Selected"
3. **Clear All**: Click "Clear All" to remove all items

## Extending the Application

### Adding a New Model

1. Create a new file in `airobo_trainer/models/`
2. Implement your model class with data operations
3. Add to `airobo_trainer/models/__init__.py`

### Adding a New View

1. Create a new file in `airobo_trainer/views/`
2. Implement your view class inheriting from QWidget or QMainWindow
3. Define signals for user interactions
4. Add to `airobo_trainer/views/__init__.py`

### Adding a New Controller

1. Create a new file in `airobo_trainer/controllers/`
2. Implement your controller class
3. Connect View signals to Model operations
4. Add to `airobo_trainer/controllers/__init__.py`

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Acknowledgments

- Built with [PyQt6](https://www.riverbankcomputing.com/software/pyqt/)
- Testing with [pytest](https://pytest.org/) and [pytest-qt](https://pytest-qt.readthedocs.io/)
