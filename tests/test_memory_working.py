"""Unit tests for Working Memory module."""

import time

from src.memory.working import WorkingMemory


class TestWorkingMemory:
    """Test suite for Working Memory module."""

    def test_initialization(self):
        """Test working memory initialization."""
        memory = WorkingMemory(ttl_seconds=3600)
        assert len(memory) == 0
        assert memory._ttl_seconds == 3600

    def test_set_and_get(self):
        """Test basic set and get operations."""
        memory = WorkingMemory()

        # Set a value
        memory.set("test_key", "test_value")

        # Get the value
        value = memory.get("test_key")
        assert value == "test_value"

    def test_get_nonexistent_key(self):
        """Test getting a non-existent key returns None."""
        memory = WorkingMemory()
        value = memory.get("nonexistent")
        assert value is None

    def test_set_with_custom_ttl(self):
        """Test setting with custom TTL."""
        memory = WorkingMemory(ttl_seconds=3600)

        # Set with custom TTL
        memory.set("test_key", "test_value", ttl=7200)

        # Check it's stored
        value = memory.get("test_key")
        assert value == "test_value"

    def test_expiry(self):
        """Test that entries expire after TTL."""
        memory = WorkingMemory(ttl_seconds=1)  # 1 second TTL

        # Set a value
        memory.set("test_key", "test_value")

        # Should be retrievable immediately
        assert memory.get("test_key") == "test_value"

        # Wait for expiry
        time.sleep(1.1)

        # Should be None after expiry
        assert memory.get("test_key") is None

    def test_delete(self):
        """Test deleting entries."""
        memory = WorkingMemory()

        # Set a value
        memory.set("test_key", "test_value")
        assert memory.get("test_key") == "test_value"

        # Delete it
        result = memory.delete("test_key")
        assert result is True

        # Should be None now
        assert memory.get("test_key") is None

    def test_delete_nonexistent(self):
        """Test deleting non-existent key returns False."""
        memory = WorkingMemory()
        result = memory.delete("nonexistent")
        assert result is False

    def test_clear(self):
        """Test clearing all entries."""
        memory = WorkingMemory()

        # Add multiple entries
        memory.set("key1", "value1")
        memory.set("key2", "value2")
        memory.set("key3", "value3")

        assert len(memory) == 3

        # Clear all
        memory.clear()

        assert len(memory) == 0
        assert memory.get("key1") is None

    def test_cleanup_expired(self):
        """Test manual cleanup of expired entries."""
        memory = WorkingMemory(ttl_seconds=1)

        # Add entries
        memory.set("key1", "value1")
        memory.set("key2", "value2")

        # Wait for expiry
        time.sleep(1.1)

        # Add a new entry that hasn't expired
        memory.set("key3", "value3")

        # Cleanup expired
        removed = memory.cleanup_expired()

        # Should have removed 2 entries
        assert removed == 2

        # key3 should still be there
        assert memory.get("key3") == "value3"
        assert memory.get("key1") is None

    def test_get_all_keys(self):
        """Test getting all non-expired keys."""
        memory = WorkingMemory(ttl_seconds=1)

        # Add entries
        memory.set("key1", "value1")
        memory.set("key2", "value2")

        # Get all keys
        keys = memory.get_all_keys()
        assert "key1" in keys
        assert "key2" in keys
        assert len(keys) == 2

        # Wait for expiry
        time.sleep(1.1)

        # Add new entry
        memory.set("key3", "value3")

        # Should only return non-expired keys
        keys = memory.get_all_keys()
        assert "key3" in keys
        assert "key1" not in keys
        assert len(keys) == 1

    def test_len(self):
        """Test __len__ method."""
        memory = WorkingMemory()

        assert len(memory) == 0

        memory.set("key1", "value1")
        assert len(memory) == 1

        memory.set("key2", "value2")
        assert len(memory) == 2

        memory.delete("key1")
        assert len(memory) == 1

    def test_repr(self):
        """Test __repr__ method."""
        memory = WorkingMemory(ttl_seconds=3600)
        memory.set("key1", "value1")

        repr_str = repr(memory)
        assert "WorkingMemory" in repr_str
        assert "entries=1" in repr_str
        assert "ttl=3600" in repr_str

    def test_complex_values(self):
        """Test storing complex data types."""
        memory = WorkingMemory()

        # Dictionary
        memory.set("dict_key", {"nested": {"data": "value"}})
        assert memory.get("dict_key") == {"nested": {"data": "value"}}

        # List
        memory.set("list_key", [1, 2, 3, 4, 5])
        assert memory.get("list_key") == [1, 2, 3, 4, 5]

        # Object
        class TestObject:
            def __init__(self):
                self.attr = "value"

        obj = TestObject()
        memory.set("obj_key", obj)
        retrieved = memory.get("obj_key")
        assert retrieved.attr == "value"

    def test_concurrent_access(self):
        """Test that memory handles multiple operations correctly."""
        memory = WorkingMemory()

        # Simulate multiple "concurrent" operations
        for i in range(100):
            memory.set(f"key_{i}", f"value_{i}")

        # All should be retrievable
        for i in range(100):
            assert memory.get(f"key_{i}") == f"value_{i}"

        # Length should be correct
        assert len(memory) == 100

    def test_overwrite_existing_key(self):
        """Test that setting an existing key overwrites the value."""
        memory = WorkingMemory()

        memory.set("key", "value1")
        assert memory.get("key") == "value1"

        memory.set("key", "value2")
        assert memory.get("key") == "value2"

    def test_global_instance(self):
        """Test that global working memory instance is available."""
        from src.memory.working import working_memory

        # Should be a WorkingMemory instance
        assert isinstance(working_memory, WorkingMemory)

        # Should be usable
        working_memory.set("test", "value")
        assert working_memory.get("test") == "value"

        # Clean up
        working_memory.clear()
