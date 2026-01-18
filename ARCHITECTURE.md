# AiRobo-Trainer Architecture Documentation

**Stroke Rehabilitation Trainer powered by Brain-Computer Interface (BCI)**

## MVC Pattern Implementation

This medical application follows a strict Model-View-Controller (MVC) architecture pattern, ensuring reliability, maintainability, and testability required for healthcare software.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         main.py                              │
│            (BCI Rehabilitation Entry Point)                  │
│  - Creates QApplication                                      │
│  - Initializes MainController                                │
│  - Starts BCI configuration interface                        │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          │ creates
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                   MainController                             │
│            (TRAINING MODULE CONTROLLER)                      │
│  - Initializes Model and View                                │
│  - Manages training module configuration                     │
│  - Handles BCI session logic                                 │
│  - Coordinates Model ↔ View                                  │
└──────────┬────────────────────────────────┬─────────────────┘
           │                                │
           │ uses                           │ uses
           ▼                                ▼
┌──────────────────────┐         ┌────────────────────────────┐
│     ItemModel        │         │       MainView             │
│     (MODEL)          │         │       (VIEW)               │
│                      │         │                            │
│  Training Config:    │         │  Configure BCI Interface:  │
│  - Prepopulated:     │         │  - QMainWindow             │
│    • Text Commands   │         │  - Title: "Configure BCI"  │
│    • Avatar          │         │  - QListWidget             │
│    • Video           │         │  - QPushButton (Remove)    │
│  - remove_item()     │         │  - QPushButton (Clear)     │
│  - get_item()        │         │  - QLabel (Status)         │
│  - get_all_items()   │         │                            │
│  - clear_all()       │         │  Signals:                  │
│  - get_count()       │         │  - remove_item_requested   │
│                      │         │  - clear_all_requested     │
│  No UI dependencies  │         │                            │
│  Pure data logic     │         │  Clinical interface design │
└──────────────────────┘         └────────────────────────────┘
```

## Component Responsibilities

### Model Layer (item_model.py)
**Responsibility**: BCI training module configuration data management

**What it does**:
- Stores and manages rehabilitation training modules
- Prepopulated with three core modules:
  - Text Commands (cognitive rehabilitation)
  - Avatar (motor skill recovery)
  - Video (visual feedback exercises)
- Provides data operations (remove, get, clear)
- Maintains data integrity for training sessions

**What it does NOT do**:
- No UI code
- No Qt dependencies
- No signal handling
- No user interaction logic

**Key Methods**:
```python
__init__() -> None  # Prepopulates training modules
remove_item(index: int) -> bool
get_item(index: int) -> Optional[str]
get_all_items() -> List[str]
clear_all() -> None
get_count() -> int
```

### View Layer (main_view.py)
**Responsibility**: BCI configuration user interface

**What it does**:
- Displays "Configure BCI" clinical interface
- Shows available training modules in list widget
- Provides module management controls
- Emits signals when healthcare professional interacts
- Updates display when configuration changes
- Shows dialogs for feedback and warnings

**What it does NOT do**:
- No business logic
- No data validation
- No direct model manipulation
- No decision making

**Key Components**:
```python
# UI Widgets
title_label: QLabel  # "Configure BCI"
list_widget: QListWidget  # Training modules
remove_button: QPushButton  # Top, full width
clear_button: QPushButton  # Bottom, full width
status_label: QLabel  # Session status

# Signals (emitted to controller)
remove_item_requested = pyqtSignal(int)
clear_all_requested = pyqtSignal()

# Update methods (called by controller)
update_list(items: List[str])
set_status(message: str)
show_warning(title: str, message: str)
```

### Controller Layer (main_controller.py)
**Responsibility**: BCI training session logic and coordination

**What it does**:
- Creates Model and View instances for BCI configuration
- Connects UI signals to training module handlers
- Manages training module removal and clearing logic
- Updates interface based on configuration state
- Provides status feedback to healthcare professionals
- Ensures configuration consistency for rehabilitation sessions

**What it does NOT do**:
- No direct UI widget manipulation (delegates to View)
- No direct data structure manipulation (delegates to Model)

**Key Methods**:
```python
# Initialization
__init__(model, view)
_connect_signals()
_update_view()
_update_status()

# Signal handlers (private)
_handle_remove_item(index: int)
_handle_clear_all()

# Public interface
show()
get_model() -> ItemModel
get_view() -> MainView
```

## Data Flow

### Adding an Item
```
1. User types "New Item" and clicks "Add" button
   │
   ▼
2. MainView.add_button.clicked signal
   │
   ▼
3. MainView emits add_item_requested("New Item")
   │
   ▼
4. MainController._handle_add_item("New Item")
   │
   ├─> Validates input (not empty, not duplicate)
   │
   ├─> If invalid: view.show_warning()
   │
   └─> If valid:
       │
       ├─> model.add_item("New Item")
       │
       ├─> view.update_list(model.get_all_items())
       │
       ├─> view.clear_input()
       │
       └─> view.set_status("Added: New Item")
```

### Removing an Item
```
1. User selects item and clicks "Remove Selected" button
   │
   ▼
2. MainView.remove_button.clicked signal
   │
   ▼
3. MainView emits remove_item_requested(index)
   │
   ▼
4. MainController._handle_remove_item(index)
   │
   ├─> Gets item name: model.get_item(index)
   │
   ├─> Removes item: model.remove_item(index)
   │
   ├─> Updates view: view.update_list(model.get_all_items())
   │
   └─> Updates status: view.set_status("Removed: Item Name")
```

## Signal-Slot Architecture

```
View (Signals)              Controller (Slots)           Model (Methods)
─────────────              ──────────────────           ───────────────

add_item_requested    →    _handle_add_item        →    add_item()
                                                    ←    returns success
                           validates & decides
                                │
                                ├─> view.show_warning()
                                └─> view.update_list()

remove_item_requested →    _handle_remove_item     →    remove_item()
                                                    ←    returns success
                           handles response
                                │
                                └─> view.update_list()

clear_all_requested   →    _handle_clear_all       →    clear_all()
                           updates UI
                                │
                                └─> view.update_list()
```

## Testing Strategy

### Unit Tests for Model (test_item_model.py)
- Test each method independently
- No Qt dependencies required
- Fast execution
- Examples: test_add_item_success, test_add_duplicate_item

### Unit Tests for View (test_main_view.py)
- Uses pytest-qt (qtbot fixture)
- Tests UI components and signals
- Mocks QMessageBox dialogs
- Examples: test_add_button_clicked_signal, test_update_list

### Integration Tests for Controller (test_main_controller.py)
- Tests Model-View coordination
- Uses both qtbot and monkeypatch
- Tests complete workflows
- Examples: test_handle_add_item_success, test_signal_connections

## Design Principles Applied

1. **Separation of Concerns**
   - Each layer has distinct responsibility
   - No cross-layer dependencies (Model doesn't know View exists)

2. **Single Responsibility Principle**
   - Model: Data only
   - View: UI only
   - Controller: Coordination only

3. **Dependency Inversion**
   - Controller depends on abstractions (Model/View interfaces)
   - Can inject mock objects for testing

4. **Signals and Slots**
   - Loose coupling between components
   - Qt's event-driven architecture

5. **Type Safety**
   - Full type hints for all methods
   - Better IDE support and error detection

6. **Testability**
   - Each component can be tested independently
   - Comprehensive test coverage

## Benefits of This Architecture

1. **Maintainability**: Easy to locate and fix bugs
2. **Scalability**: Easy to add new features
3. **Testability**: Each layer tested independently
4. **Flexibility**: Easy to swap implementations
5. **Reusability**: Components can be reused
6. **Team Development**: Clear boundaries for parallel work

## Extending the Application

### Adding a New Feature: "Export to File"

1. **Model**: Add method
```python
def export_to_file(self, filepath: str) -> bool:
    # Implementation
```

2. **View**: Add button
```python
export_requested = pyqtSignal(str)
self.export_button = QPushButton("Export")
```

3. **Controller**: Add handler
```python
def _handle_export(self, filepath: str):
    success = self.model.export_to_file(filepath)
    if success:
        self.view.show_info("Success", "Exported!")
```

4. **Test**: Add tests
```python
def test_export_to_file(self, model):
    # Test implementation
```

## Common Patterns

### Error Handling
```python
# Controller always handles errors
def _handle_operation(self):
    if not self._validate():
        self.view.show_warning("Error", "Message")
        return

    success = self.model.operation()
    if success:
        self._update_view()
    else:
        self.view.show_error("Error", "Failed")
```

### Status Updates
```python
# Controller manages status display
def _update_status(self):
    count = self.model.get_count()
    self.view.set_status(f"{count} items")
```

### View Updates
```python
# Always refresh entire view from model
def _update_view(self):
    items = self.model.get_all_items()
    self.view.update_list(items)
    self._update_status()
```

## Best Practices Followed

1. Private methods prefixed with `_`
2. Type hints on all methods
3. Docstrings for all public methods
4. No magic numbers or strings
5. Consistent naming conventions
6. Comprehensive error handling
7. Complete test coverage
8. No circular dependencies
9. Clear separation of concerns
10. DRY (Don't Repeat Yourself) principle
