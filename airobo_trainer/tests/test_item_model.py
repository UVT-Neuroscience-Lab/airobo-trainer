"""
Unit tests for ItemModel
"""

import pytest

from airobo_trainer.models.item_model import ItemModel


class TestItemModel:
    """Test suite for the ItemModel class."""

    @pytest.fixture
    def model(self):
        """Create a fresh ItemModel instance for each test."""
        return ItemModel()

    def test_init(self, model):
        """Test model initialization with prepopulated items."""
        assert model.get_count() == 3
        assert model.get_all_items() == ["Text Commands", "Avatar", "Video"]

    def test_get_item_success(self, model):
        """Test successfully retrieving an item."""
        item = model.get_item(0)
        assert item == "Text Commands"

    def test_get_item_invalid_index(self, model):
        """Test retrieving an item with invalid index."""
        item = model.get_item(5)
        assert item is None

    def test_get_all_items(self, model):
        """Test retrieving all items."""
        items = model.get_all_items()
        assert items == ["Text Commands", "Avatar", "Video"]

    def test_get_all_items_returns_copy(self, model):
        """Test that get_all_items returns a copy, not a reference."""
        items = model.get_all_items()
        items.append("New Item")
        assert model.get_count() == 3

    def test_remove_item_success(self, model):
        """Test successfully removing an item."""
        result = model.remove_item(0)
        assert result is True
        assert model.get_count() == 2
        assert model.get_item(0) == "Avatar"

    def test_remove_item_invalid_index(self, model):
        """Test removing an item with invalid index."""
        result = model.remove_item(5)
        assert result is False
        assert model.get_count() == 3

    def test_remove_item_negative_index(self, model):
        """Test removing an item with negative index."""
        result = model.remove_item(-1)
        assert result is False
        assert model.get_count() == 3

    def test_clear_all(self, model):
        """Test clearing all items."""
        model.clear_all()
        assert model.get_count() == 0
        assert model.get_all_items() == []

    def test_get_count(self, model):
        """Test getting item count."""
        assert model.get_count() == 3
        model.remove_item(0)
        assert model.get_count() == 2
        model.clear_all()
        assert model.get_count() == 0
