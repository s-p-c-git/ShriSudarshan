"""Unit tests for Procedural Memory module."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os

from src.memory.procedural import ProceduralMemory, CHROMA_AVAILABLE


class TestProceduralMemory:
    """Test suite for Procedural Memory module."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for ChromaDB."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        # Cleanup
        import shutil
        try:
            shutil.rmtree(temp_dir)
        except:
            pass
    
    def test_initialization_without_chroma(self):
        """Test initialization when ChromaDB is not available."""
        with patch('src.memory.procedural.CHROMA_AVAILABLE', False):
            memory = ProceduralMemory()
            assert memory.client is None
            assert memory.collection is None
    
    @pytest.mark.skipif(not CHROMA_AVAILABLE, reason="ChromaDB not installed")
    def test_initialization_with_chroma(self, temp_dir):
        """Test initialization with ChromaDB available."""
        memory = ProceduralMemory(persist_directory=temp_dir)
        
        # Should have initialized client and collection
        assert memory.client is not None
        assert memory.collection is not None
    
    @pytest.mark.skipif(not CHROMA_AVAILABLE, reason="ChromaDB not installed")
    def test_store_pattern(self, temp_dir):
        """Test storing a pattern."""
        memory = ProceduralMemory(persist_directory=temp_dir)
        
        memory.store_pattern(
            pattern_id="pattern-001",
            description="Successful bullish strategy in uptrend",
            context={"market_condition": "uptrend", "volatility": "low"},
            success_metrics={"return": 15.5, "win_rate": 0.75},
        )
        
        # Verify pattern can be retrieved
        pattern = memory.get_pattern("pattern-001")
        assert pattern is not None
        assert pattern['id'] == "pattern-001"
        assert "uptrend" in pattern['description']
    
    @pytest.mark.skipif(not CHROMA_AVAILABLE, reason="ChromaDB not installed")
    def test_search_similar_patterns(self, temp_dir):
        """Test searching for similar patterns."""
        memory = ProceduralMemory(persist_directory=temp_dir)
        
        # Store multiple patterns
        patterns = [
            {
                "pattern_id": "pattern-001",
                "description": "Bullish strategy in strong uptrend with low volatility",
                "context": {"market": "uptrend"},
                "success_metrics": {"return": 15.5},
            },
            {
                "pattern_id": "pattern-002",
                "description": "Bearish strategy in downtrend with high volatility",
                "context": {"market": "downtrend"},
                "success_metrics": {"return": 12.0},
            },
            {
                "pattern_id": "pattern-003",
                "description": "Neutral strategy in sideways market",
                "context": {"market": "sideways"},
                "success_metrics": {"return": 5.0},
            },
        ]
        
        for pattern in patterns:
            memory.store_pattern(**pattern)
        
        # Search for bullish patterns
        results = memory.search_similar_patterns("bullish uptrend strategy", n_results=2)
        
        assert len(results) > 0
        # First result should be most similar
        assert "pattern-001" in results[0]['id'] or "Bullish" in results[0]['description']
    
    @pytest.mark.skipif(not CHROMA_AVAILABLE, reason="ChromaDB not installed")
    def test_get_pattern(self, temp_dir):
        """Test retrieving a specific pattern."""
        memory = ProceduralMemory(persist_directory=temp_dir)
        
        memory.store_pattern(
            pattern_id="test-pattern",
            description="Test pattern",
            context={"test": True},
            success_metrics={"score": 1.0},
        )
        
        pattern = memory.get_pattern("test-pattern")
        
        assert pattern is not None
        assert pattern['id'] == "test-pattern"
        assert pattern['description'] == "Test pattern"
    
    @pytest.mark.skipif(not CHROMA_AVAILABLE, reason="ChromaDB not installed")
    def test_get_nonexistent_pattern(self, temp_dir):
        """Test getting a pattern that doesn't exist."""
        memory = ProceduralMemory(persist_directory=temp_dir)
        
        pattern = memory.get_pattern("nonexistent")
        assert pattern is None
    
    @pytest.mark.skipif(not CHROMA_AVAILABLE, reason="ChromaDB not installed")
    def test_delete_pattern(self, temp_dir):
        """Test deleting a pattern."""
        memory = ProceduralMemory(persist_directory=temp_dir)
        
        # Store pattern
        memory.store_pattern(
            pattern_id="to-delete",
            description="Pattern to be deleted",
            context={},
            success_metrics={},
        )
        
        # Verify it exists
        assert memory.get_pattern("to-delete") is not None
        
        # Delete it
        result = memory.delete_pattern("to-delete")
        assert result is True
        
        # Verify it's gone
        assert memory.get_pattern("to-delete") is None
    
    @pytest.mark.skipif(not CHROMA_AVAILABLE, reason="ChromaDB not installed")
    def test_repr(self, temp_dir):
        """Test __repr__ method."""
        memory = ProceduralMemory(persist_directory=temp_dir)
        
        # Store a pattern
        memory.store_pattern(
            pattern_id="test",
            description="Test",
            context={},
            success_metrics={},
        )
        
        repr_str = repr(memory)
        assert "ProceduralMemory" in repr_str
        assert "patterns=" in repr_str


class TestProceduralMemoryMockMode:
    """Test procedural memory in mock mode (no ChromaDB)."""
    
    def test_store_pattern_mock_mode(self):
        """Test storing pattern in mock mode."""
        with patch('src.memory.procedural.CHROMA_AVAILABLE', False):
            memory = ProceduralMemory()
            
            # Should not raise error
            memory.store_pattern(
                pattern_id="test",
                description="Test",
                context={},
                success_metrics={},
            )
    
    def test_search_patterns_mock_mode(self):
        """Test searching patterns in mock mode."""
        with patch('src.memory.procedural.CHROMA_AVAILABLE', False):
            memory = ProceduralMemory()
            
            results = memory.search_similar_patterns("test query")
            assert results == []
    
    def test_get_pattern_mock_mode(self):
        """Test getting pattern in mock mode."""
        with patch('src.memory.procedural.CHROMA_AVAILABLE', False):
            memory = ProceduralMemory()
            
            pattern = memory.get_pattern("test")
            assert pattern is None
    
    def test_delete_pattern_mock_mode(self):
        """Test deleting pattern in mock mode."""
        with patch('src.memory.procedural.CHROMA_AVAILABLE', False):
            memory = ProceduralMemory()
            
            result = memory.delete_pattern("test")
            assert result is False
