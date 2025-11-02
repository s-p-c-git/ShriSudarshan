"""Unit tests for Episodic Memory module."""

import pytest
import tempfile
import os
from datetime import datetime, timedelta

from src.memory.episodic import EpisodicMemory
from src.data.schemas import TradeOutcome, Reflection, StrategyType


class TestEpisodicMemory:
    """Test suite for Episodic Memory module."""
    
    @pytest.fixture
    def temp_db(self):
        """Create a temporary database for testing."""
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        db_url = f"sqlite:///{temp_file.name}"
        temp_file.close()
        
        yield db_url
        
        # Cleanup
        try:
            os.unlink(temp_file.name)
        except:
            pass
    
    @pytest.fixture
    def memory(self, temp_db):
        """Create episodic memory instance with temp database."""
        return EpisodicMemory(database_url=temp_db)
    
    @pytest.fixture
    def sample_trade_outcome(self):
        """Sample trade outcome for testing."""
        return TradeOutcome(
            trade_id="TRADE-001",
            symbol="AAPL",
            strategy_type=StrategyType.LONG_EQUITY,
            entry_date=datetime.now() - timedelta(days=30),
            exit_date=datetime.now(),
            entry_price=150.00,
            exit_price=165.00,
            quantity=100,
            realized_pnl=1500.00,
            return_pct=10.0,
            outcome="win",
            notes="Successful trade following technical analysis",
        )
    
    @pytest.fixture
    def sample_reflection(self):
        """Sample reflection for testing."""
        return Reflection(
            trade_id="TRADE-001",
            symbol="AAPL",
            analysis_summary="Trade executed well with good timing",
            what_worked=["Technical analysis", "Patient entry"],
            what_failed=["Could have held longer"],
            lessons_learned=["Use trailing stops"],
            strategic_recommendations=["Increase position size for high confidence"],
        )
    
    def test_initialization(self, memory):
        """Test episodic memory initialization."""
        assert memory.database_url is not None
        assert memory.engine is not None
        
        # Tables should be created
        from sqlalchemy import inspect
        inspector = inspect(memory.engine)
        tables = inspector.get_table_names()
        assert "trades" in tables
        assert "reflections" in tables
    
    def test_store_trade(self, memory, sample_trade_outcome):
        """Test storing a trade outcome."""
        # Store trade
        memory.store_trade(sample_trade_outcome)
        
        # Retrieve it
        retrieved = memory.get_trade("TRADE-001")
        
        assert retrieved is not None
        assert retrieved.trade_id == "TRADE-001"
        assert retrieved.symbol == "AAPL"
        assert retrieved.strategy_type == StrategyType.LONG_EQUITY
        assert retrieved.realized_pnl == 1500.00
    
    def test_store_multiple_trades(self, memory):
        """Test storing multiple trades."""
        trades = [
            TradeOutcome(
                trade_id=f"TRADE-{i:03d}",
                symbol="AAPL",
                strategy_type=StrategyType.LONG_EQUITY,
                entry_date=datetime.now() - timedelta(days=i),
                entry_price=150.00 + i,
                quantity=100,
                outcome="pending",
            )
            for i in range(5)
        ]
        
        for trade in trades:
            memory.store_trade(trade)
        
        # Verify all stored
        for i in range(5):
            retrieved = memory.get_trade(f"TRADE-{i:03d}")
            assert retrieved is not None
    
    def test_get_nonexistent_trade(self, memory):
        """Test getting a non-existent trade returns None."""
        result = memory.get_trade("NONEXISTENT")
        assert result is None
    
    def test_get_trades_by_symbol(self, memory):
        """Test getting trades filtered by symbol."""
        # Store trades for different symbols
        symbols = ["AAPL", "AAPL", "MSFT", "AAPL", "GOOGL"]
        for i, symbol in enumerate(symbols):
            trade = TradeOutcome(
                trade_id=f"TRADE-{i:03d}",
                symbol=symbol,
                strategy_type=StrategyType.LONG_EQUITY,
                entry_date=datetime.now() - timedelta(days=i),
                entry_price=150.00,
                quantity=100,
                outcome="pending",
            )
            memory.store_trade(trade)
        
        # Get AAPL trades
        aapl_trades = memory.get_trades_by_symbol("AAPL")
        assert len(aapl_trades) == 3
        assert all(t.symbol == "AAPL" for t in aapl_trades)
        
        # Get MSFT trades
        msft_trades = memory.get_trades_by_symbol("MSFT")
        assert len(msft_trades) == 1
    
    def test_get_trades_by_symbol_limit(self, memory):
        """Test limit parameter in get_trades_by_symbol."""
        # Store 10 trades
        for i in range(10):
            trade = TradeOutcome(
                trade_id=f"TRADE-{i:03d}",
                symbol="AAPL",
                strategy_type=StrategyType.LONG_EQUITY,
                entry_date=datetime.now() - timedelta(days=i),
                entry_price=150.00,
                quantity=100,
                outcome="pending",
            )
            memory.store_trade(trade)
        
        # Get with limit
        trades = memory.get_trades_by_symbol("AAPL", limit=5)
        assert len(trades) == 5
    
    def test_get_trades_by_symbol_order(self, memory):
        """Test trades are returned in reverse chronological order."""
        dates = [
            datetime.now() - timedelta(days=10),
            datetime.now() - timedelta(days=5),
            datetime.now() - timedelta(days=1),
        ]
        
        for i, date in enumerate(dates):
            trade = TradeOutcome(
                trade_id=f"TRADE-{i:03d}",
                symbol="AAPL",
                strategy_type=StrategyType.LONG_EQUITY,
                entry_date=date,
                entry_price=150.00,
                quantity=100,
                outcome="pending",
            )
            memory.store_trade(trade)
        
        trades = memory.get_trades_by_symbol("AAPL")
        
        # Should be ordered newest first
        assert trades[0].entry_date > trades[1].entry_date
        assert trades[1].entry_date > trades[2].entry_date
    
    def test_store_reflection(self, memory, sample_trade_outcome, sample_reflection):
        """Test storing a reflection."""
        # Store trade first
        memory.store_trade(sample_trade_outcome)
        
        # Store reflection
        memory.store_reflection(sample_reflection)
        
        # Retrieve reflections
        reflections = memory.get_reflections_for_trade("TRADE-001")
        
        assert len(reflections) > 0
        assert reflections[0].trade_id == "TRADE-001"
        assert len(reflections[0].what_worked) == 2
    
    def test_store_multiple_reflections(self, memory, sample_trade_outcome):
        """Test storing multiple reflections for same trade."""
        memory.store_trade(sample_trade_outcome)
        
        # Store multiple reflections
        for i in range(3):
            reflection = Reflection(
                trade_id="TRADE-001",
                symbol="AAPL",
                analysis_summary=f"Reflection {i}",
                what_worked=[f"Item {i}"],
            )
            memory.store_reflection(reflection)
        
        reflections = memory.get_reflections_for_trade("TRADE-001")
        assert len(reflections) == 3
    
    def test_get_reflections_nonexistent_trade(self, memory):
        """Test getting reflections for non-existent trade."""
        reflections = memory.get_reflections_for_trade("NONEXISTENT")
        assert reflections == []
    
    def test_performance_statistics_empty(self, memory):
        """Test performance statistics with no trades."""
        stats = memory.get_performance_statistics()
        
        assert stats['total_trades'] == 0
        assert stats['closed_trades'] == 0
        assert stats['win_rate'] == 0.0
        assert stats['avg_pnl'] == 0.0
    
    def test_performance_statistics_with_trades(self, memory):
        """Test performance statistics calculation."""
        # Store winning trades
        for i in range(3):
            trade = TradeOutcome(
                trade_id=f"WIN-{i}",
                symbol="AAPL",
                strategy_type=StrategyType.LONG_EQUITY,
                entry_date=datetime.now() - timedelta(days=30),
                exit_date=datetime.now() - timedelta(days=i),
                entry_price=150.00,
                exit_price=160.00,
                quantity=100,
                realized_pnl=1000.00,
                return_pct=6.67,
                outcome="win",
            )
            memory.store_trade(trade)
        
        # Store losing trades
        for i in range(2):
            trade = TradeOutcome(
                trade_id=f"LOSS-{i}",
                symbol="AAPL",
                strategy_type=StrategyType.LONG_EQUITY,
                entry_date=datetime.now() - timedelta(days=30),
                exit_date=datetime.now() - timedelta(days=i),
                entry_price=150.00,
                exit_price=145.00,
                quantity=100,
                realized_pnl=-500.00,
                return_pct=-3.33,
                outcome="loss",
            )
            memory.store_trade(trade)
        
        stats = memory.get_performance_statistics()
        
        assert stats['total_trades'] == 5
        assert stats['closed_trades'] == 5
        assert stats['win_rate'] == 0.6  # 3 wins out of 5
        assert stats['total_pnl'] == 2000.00  # 3*1000 - 2*500
        assert stats['avg_pnl'] == 400.00  # 2000 / 5
    
    def test_performance_statistics_ignores_pending(self, memory):
        """Test that pending trades are not included in statistics."""
        # Store pending trade
        trade = TradeOutcome(
            trade_id="PENDING-1",
            symbol="AAPL",
            strategy_type=StrategyType.LONG_EQUITY,
            entry_date=datetime.now(),
            entry_price=150.00,
            quantity=100,
            outcome="pending",
        )
        memory.store_trade(trade)
        
        # Store closed trade
        trade2 = TradeOutcome(
            trade_id="CLOSED-1",
            symbol="AAPL",
            strategy_type=StrategyType.LONG_EQUITY,
            entry_date=datetime.now() - timedelta(days=30),
            exit_date=datetime.now(),
            entry_price=150.00,
            exit_price=160.00,
            quantity=100,
            realized_pnl=1000.00,
            outcome="win",
        )
        memory.store_trade(trade2)
        
        stats = memory.get_performance_statistics()
        
        assert stats['total_trades'] == 2
        assert stats['closed_trades'] == 1  # Only closed trade
    
    def test_repr(self, memory):
        """Test __repr__ method."""
        # Store a winning trade
        trade = TradeOutcome(
            trade_id="TRADE-001",
            symbol="AAPL",
            strategy_type=StrategyType.LONG_EQUITY,
            entry_date=datetime.now() - timedelta(days=30),
            exit_date=datetime.now(),
            entry_price=150.00,
            exit_price=160.00,
            quantity=100,
            realized_pnl=1000.00,
            outcome="win",
        )
        memory.store_trade(trade)
        
        repr_str = repr(memory)
        assert "EpisodicMemory" in repr_str
        assert "trades=1" in repr_str
        assert "100.00%" in repr_str  # 100% win rate


class TestEpisodicMemoryIntegration:
    """Integration tests for episodic memory."""
    
    def test_trade_reflection_workflow(self):
        """Test complete workflow of storing trade and reflections."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as temp_file:
            db_url = f"sqlite:///{temp_file.name}"
        
        try:
            memory = EpisodicMemory(database_url=db_url)
            
            # Store trade
            trade = TradeOutcome(
                trade_id="TRADE-001",
                symbol="AAPL",
                strategy_type=StrategyType.COVERED_CALL,
                entry_date=datetime.now() - timedelta(days=30),
                exit_date=datetime.now(),
                entry_price=150.00,
                exit_price=160.00,
                quantity=100,
                realized_pnl=1000.00,
                return_pct=6.67,
                outcome="win",
                notes="Successful covered call strategy",
            )
            memory.store_trade(trade)
            
            # Store reflection
            reflection = Reflection(
                trade_id="TRADE-001",
                symbol="AAPL",
                analysis_summary="Excellent execution and timing",
                what_worked=["Technical entry", "Volatility analysis"],
                what_failed=["Could have captured more upside"],
                lessons_learned=["Use higher strikes in strong uptrends"],
                strategic_recommendations=["Scale position size"],
            )
            memory.store_reflection(reflection)
            
            # Verify retrieval
            retrieved_trade = memory.get_trade("TRADE-001")
            assert retrieved_trade is not None
            assert retrieved_trade.outcome == "win"
            
            retrieved_reflections = memory.get_reflections_for_trade("TRADE-001")
            assert len(retrieved_reflections) == 1
            assert len(retrieved_reflections[0].what_worked) == 2
            
            # Check statistics
            stats = memory.get_performance_statistics()
            assert stats['win_rate'] == 1.0
            
        finally:
            # Cleanup
            try:
                os.unlink(temp_file.name)
            except:
                pass
