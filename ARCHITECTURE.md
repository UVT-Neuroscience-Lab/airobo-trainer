# AiRobo-Trainer Architecture Documentation

## MVC Pattern Implementation

This application follows a strict Model-View-Controller (MVC) architecture pattern.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         main.py                              │
│                    (Entry Point)                             │
│  - Creates QApplication                                      │
│  - Initializes MainController                                │
│  - Starts event loop                                         │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          │ creates
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                   MainController                             │
│                   (CONTROLLER)                               │
│  - Initializes Model and View                                │
│  - Connects signals to slots                                 │
│  - Handles business logic                                    │
│  - Coordinates Model ↔ View                                  │
└──────────┬────────────────────────────────┬─────────────────┘
           │                                │
           │ uses                           │ uses
           ▼                                ▼
┌──────────────────────┐         ┌────────────────────────────┐
│     ItemModel        │         │       MainView             │
│     (MODEL)          │         │       (VIEW)               │
│                      │         │                            │
│  Data Management:    │         │  UI Components:            │
│  - add_item()        │         │  - QMainWindow             │
│  - remove_item()     │         │  - QListWidget             │
│  - get_item()        │         │  - QLineEdit               │
│  - get_all_items()   │         │  - QPushButton (Add)       │
│  - clear_all()       │         │  - QPushButton (Remove)    │
│  - get_count()       │         │  - QPushButton (Clear)     │
│  - contains()        │         │  - QLabel (Status)         │
│                      │         │                            │
│  No UI dependencies  │         │  Signals:                  │
│  Pure data logic     │         │  - add_item_requested      │
│                      │         │  - remove_item_requested   │
│                      │         │  - clear_all_requested     │
└──────────────────────┘         └────────────────────────────┘
```

## Component Responsibilities

### Model Layer (item_model.py)
**Responsibility**: Data management and business rules

**What it does**:
- Stores and manages list of items
- Validates data (no empty strings, no duplicates)
- Provides data operations (add, remove, get, clear)
- Maintains data integrity

**What it does NOT do**:
- No UI code
- No Qt dependencies
- No signal handling
- No user interaction logic

**Key Methods**:
```python
add_item(item: str) -> bool
remove_item(index: int) -> bool
get_item(index: int) -> Optional[str]
get_all_items() -> List[str]
clear_all() -> None
get_count() -> int
contains(item: str) -> bool
```

### View Layer (main_view.py)
**Responsibility**: User interface and presentation

**What it does**:
- Creates and manages UI widgets
- Handles layout and styling
- Emits signals when user interacts
- Updates display when requested
- Shows dialogs (info, warning, error)

**What it does NOT do**:
- No business logic
- No data validation
- No direct model manipulation
- No decision making

**Key Components**:
```python
# Widgets
list_widget: QListWidget
text_input: QLineEdit
add_button: QPushButton
remove_button: QPushButton
clear_button: QPushButton
status_label: QLabel

# Signals (emitted to controller)
add_item_requested = pyqtSignal(str)
remove_item_requested = pyqtSignal(int)
clear_all_requested = pyqtSignal()

# Update methods (called by controller)
update_list(items: List[str])
clear_input()
set_status(message: str)
```

### Controller Layer (main_controller.py)
**Responsibility**: Application logic and coordination

**What it does**:
- Creates Model and View instances
- Connects View signals to handler methods
- Handles business logic (validation, error handling)
- Updates View based on Model state
- Makes decisions (show warnings, update status)

**What it does NOT do**:
- No direct UI widget manipulation (delegates to View)
- No direct data structure manipulation (delegates to Model)

**Key Methods**:
```python
# Initialization
__init__(model, view)
_connect_signals()
_update_view()

# Signal handlers (private)
_handle_add_item(item: str)
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
