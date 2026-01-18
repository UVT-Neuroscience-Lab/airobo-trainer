# AiRobo-Trainer - Quick Start Guide

## Installation & Running (3 Steps)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Application
```bash
python main.py
```

### 3. Run Tests
```bash
pytest
```

## What You Get

### Clean MVC Architecture
```
Model (item_model.py)
  ↓ data operations
Controller (main_controller.py)
  ↓ connects model & view
View (main_view.py)
  ↓ displays UI
```

### Complete Test Suite
- **20+ unit tests** covering all components
- **pytest-qt** for GUI testing
- **Coverage reporting** included

### Features
- Add items to a list
- Remove selected items
- Clear all items
- Real-time status updates
- Input validation
- Duplicate detection

## File Overview

### Core Application Files
- `main.py` - Application entry point
- `airobo_trainer/models/item_model.py` - Data management (98 lines)
- `airobo_trainer/views/main_view.py` - UI layout (169 lines)
- `airobo_trainer/controllers/main_controller.py` - Logic (125 lines)

### Test Files
- `airobo_trainer/tests/test_item_model.py` - Model tests (159 lines)
- `airobo_trainer/tests/test_main_view.py` - View tests (141 lines)
- `airobo_trainer/tests/test_main_controller.py` - Controller tests (182 lines)

### Configuration Files
- `requirements.txt` - Production dependencies
- `requirements-dev.txt` - Development dependencies
- `pytest.ini` - Test configuration
- `pyproject.toml` - Tool configuration
- `setup.py` - Package setup

## Quick Commands

```bash
# Development setup
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements-dev.txt

# Run application
python main.py

# Run tests
pytest                                    # All tests
pytest -v                                 # Verbose output
pytest --cov=airobo_trainer              # With coverage
pytest airobo_trainer/tests/test_item_model.py  # Specific file

# Code quality
black airobo_trainer/                    # Format code
flake8 airobo_trainer/                   # Check style
mypy airobo_trainer/                     # Type checking
pylint airobo_trainer/                   # Linting
```

## Next Steps

1. **Customize the Model**: Add your own data structures in `models/`
2. **Design Your UI**: Modify or create new views in `views/`
3. **Add Business Logic**: Extend controllers in `controllers/`
4. **Write Tests**: Add tests for your new components in `tests/`

## Architecture Benefits

1. **Separation of Concerns**: Each component has a single responsibility
2. **Testability**: Easy to test each layer independently
3. **Maintainability**: Changes in one layer don't affect others
4. **Scalability**: Easy to add new features following the same pattern
5. **Type Safety**: Full type hints for better IDE support and fewer bugs

## Example: Adding a New Feature

1. **Model**: Add method to `ItemModel`
```python
def sort_items(self) -> None:
    self._items.sort()
```

2. **View**: Add button to `MainView`
```python
self.sort_button = QPushButton("Sort")
self.sort_button.clicked.connect(self._on_sort_clicked)
```

3. **Controller**: Connect in `MainController`
```python
self.view.sort_button.clicked.connect(self._handle_sort)

def _handle_sort(self) -> None:
    self.model.sort_items()
    self._update_view()
```

4. **Test**: Add test in `tests/`
```python
def test_sort_items(self, model):
    model.add_item("Zebra")
    model.add_item("Apple")
    model.sort_items()
    assert model.get_all_items() == ["Apple", "Zebra"]
```

## Troubleshooting

### ModuleNotFoundError: No module named 'PyQt6'
```bash
pip install PyQt6
```

### Tests not found
```bash
# Make sure you're in the project root directory
cd /path/to/airobo-trainer
pytest
```

### Application doesn't start
Check Python version (requires 3.8+):
```bash
python --version
```

## Support

- Read the full [README.md](README.md) for detailed documentation
- Check [LICENSE](LICENSE) for usage terms
- Open issues on GitHub for bugs or feature requests
