# AiRobo-Trainer - Quick Start Guide

**Stroke Rehabilitation Trainer powered by Brain-Computer Interface (BCI)**

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

### Medical-Grade MVC Architecture
```
Model (item_model.py)
  ↓ BCI training configuration data
Controller (main_controller.py)
  ↓ manages training module logic
View (main_view.py)
  ↓ Configure BCI interface
```

### Complete Test Suite
- **15+ unit tests** covering all components
- **pytest-qt** for GUI testing
- **Coverage reporting** included
- Medical-grade code quality standards

### BCI Training Features
- **Pre-configured Training Modules**: Text Commands, Avatar, Video
- **Module Management**: Remove or configure training modules for sessions
- **Real-time Status**: Live updates on configuration state
- **Healthcare Interface**: Designed for clinical and research settings

## File Overview

### Core Application Files
- `main.py` - BCI Rehabilitation application entry point
- `airobo_trainer/models/item_model.py` - Training module configuration data
- `airobo_trainer/views/main_view.py` - Configure BCI interface
- `airobo_trainer/controllers/main_controller.py` - Training module logic

### Test Files
- `airobo_trainer/tests/test_item_model.py` - Configuration model tests
- `airobo_trainer/tests/test_main_view.py` - UI interface tests
- `airobo_trainer/tests/test_main_controller.py` - Training logic tests

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

1. **Add Training Modules**: Extend rehabilitation training options in `models/`
2. **Customize UI**: Adapt the interface for specific clinical needs in `views/`
3. **Integrate BCI Hardware**: Connect brain-computer interface devices
4. **Implement Protocols**: Add patient-specific rehabilitation protocols
5. **Write Tests**: Ensure reliability with comprehensive testing

## Architecture Benefits

1. **Medical-Grade Reliability**: Strict separation ensures code safety
2. **Easy Testing**: Each layer can be independently validated
3. **Clinical Adaptability**: Simple to modify for different protocols
4. **Research-Friendly**: Clean architecture for academic studies
5. **Type Safety**: Reduces runtime errors in critical medical applications

## Example: Adding a New Training Module

1. **Model**: Update prepopulated modules in `ItemModel`
```python
def __init__(self) -> None:
    self._items: List[str] = [
        "Text Commands",
        "Avatar",
        "Video",
        "Motor Imagery"  # New module
    ]
```

2. **View**: Interface automatically displays new modules

3. **Controller**: Existing logic handles new modules automatically

4. **Test**: Add validation test in `tests/`
```python
def test_init_with_motor_imagery(self, model):
    assert "Motor Imagery" in model.get_all_items()
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

## Medical Disclaimer

This software is for research and educational purposes only. Not intended as a medical device. Consult qualified healthcare professionals for clinical use.

## Support

- Read the full [README.md](README.md) for detailed documentation
- Check [LICENSE](LICENSE) for usage terms
- Review [ARCHITECTURE.md](ARCHITECTURE.md) for technical details
- Open issues on GitHub for bugs or feature requests
