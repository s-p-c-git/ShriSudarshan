"""
Episodic Memory module for Project Shri Sudarshan.

Episodic memory stores historical trades and their outcomes
for learning and reflection.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime

from sqlalchemy import create_engine, Column, String, Float, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from ..config import settings
from ..data.schemas import TradeOutcome, Reflection

Base = declarative_base()


class TradeRecord(Base):
    """Database model for trade records."""
    __tablename__ = "trades"
    
    trade_id = Column(String, primary_key=True)
    symbol = Column(String, nullable=False)
    strategy_type = Column(String, nullable=False)
    entry_date = Column(DateTime, nullable=False)
    exit_date = Column(DateTime)
    entry_price = Column(Float, nullable=False)
    exit_price = Column(Float)
    position_size = Column(Float, nullable=False)
    pnl = Column(Float)
    pnl_percentage = Column(Float)
    rationale = Column(Text, nullable=False)
    market_conditions = Column(JSON)
    outcome_status = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)


class ReflectionRecord(Base):
    """Database model for reflection records."""
    __tablename__ = "reflections"
    
    reflection_id = Column(String, primary_key=True)
    trade_id = Column(String, nullable=False)
    accuracy_assessment = Column(Text, nullable=False)
    key_learnings = Column(JSON)
    belief_adjustments = Column(JSON)
    actionable_improvements = Column(JSON)
    created_at = Column(DateTime, default=datetime.now)


class EpisodicMemory:
    """
    SQL database storage for historical trades and reflections.
    
    Enables long-term learning through analysis of past decisions.
    """
    
    def __init__(self, database_url: Optional[str] = None):
        """
        Initialize episodic memory.
        
        Args:
            database_url: Database connection URL
        """
        self.database_url = database_url or settings.database_url
        
        # Create engine
        self.engine = create_engine(self.database_url)
        
        # Create tables
        Base.metadata.create_all(self.engine)
        
        # Create session factory
        self.SessionLocal = sessionmaker(bind=self.engine)
    
    def _get_session(self) -> Session:
        """Get a new database session."""
        return self.SessionLocal()
    
    def store_trade(self, trade: TradeOutcome) -> None:
        """
        Store a trade outcome in episodic memory.
        
        Args:
            trade: TradeOutcome object
        """
        session = self._get_session()
        try:
            record = TradeRecord(
                trade_id=trade.trade_id,
                symbol=trade.symbol,
                strategy_type=trade.strategy_type,
                entry_date=trade.entry_date,
                exit_date=trade.exit_date,
                entry_price=trade.entry_price,
                exit_price=trade.exit_price,
                position_size=trade.position_size,
                pnl=trade.pnl,
                pnl_percentage=trade.pnl_percentage,
                rationale=trade.rationale,
                market_conditions=trade.market_conditions,
                outcome_status=trade.outcome_status,
            )
            session.add(record)
            session.commit()
        finally:
            session.close()
    
    def store_reflection(self, reflection: Reflection) -> None:
        """
        Store a reflection in episodic memory.
        
        Args:
            reflection: Reflection object
        """
        session = self._get_session()
        try:
            record = ReflectionRecord(
                reflection_id=f"refl_{reflection.trade_id}_{datetime.now().timestamp()}",
                trade_id=reflection.trade_id,
                accuracy_assessment=reflection.accuracy_assessment,
                key_learnings=reflection.key_learnings,
                belief_adjustments=reflection.belief_adjustments,
                actionable_improvements=reflection.actionable_improvements,
            )
            session.add(record)
            session.commit()
        finally:
            session.close()
    
    def get_trade(self, trade_id: str) -> Optional[TradeOutcome]:
        """
        Retrieve a specific trade by ID.
        
        Args:
            trade_id: Trade identifier
            
        Returns:
            TradeOutcome or None if not found
        """
        session = self._get_session()
        try:
            record = session.query(TradeRecord).filter_by(trade_id=trade_id).first()
            if not record:
                return None
            
            return TradeOutcome(
                trade_id=record.trade_id,
                symbol=record.symbol,
                strategy_type=record.strategy_type,
                entry_date=record.entry_date,
                exit_date=record.exit_date,
                entry_price=record.entry_price,
                exit_price=record.exit_price,
                position_size=record.position_size,
                pnl=record.pnl,
                pnl_percentage=record.pnl_percentage,
                rationale=record.rationale,
                market_conditions=record.market_conditions or {},
                outcome_status=record.outcome_status,
            )
        finally:
            session.close()
    
    def get_trades_by_symbol(self, symbol: str, limit: int = 10) -> List[TradeOutcome]:
        """
        Get recent trades for a symbol.
        
        Args:
            symbol: Stock symbol
            limit: Maximum number of trades to return
            
        Returns:
            List of TradeOutcome objects
        """
        session = self._get_session()
        try:
            records = (
                session.query(TradeRecord)
                .filter_by(symbol=symbol)
                .order_by(TradeRecord.entry_date.desc())
                .limit(limit)
                .all()
            )
            
            return [
                TradeOutcome(
                    trade_id=record.trade_id,
                    symbol=record.symbol,
                    strategy_type=record.strategy_type,
                    entry_date=record.entry_date,
                    exit_date=record.exit_date,
                    entry_price=record.entry_price,
                    exit_price=record.exit_price,
                    position_size=record.position_size,
                    pnl=record.pnl,
                    pnl_percentage=record.pnl_percentage,
                    rationale=record.rationale,
                    market_conditions=record.market_conditions or {},
                    outcome_status=record.outcome_status,
                )
                for record in records
            ]
        finally:
            session.close()
    
    def get_reflections_for_trade(self, trade_id: str) -> List[Reflection]:
        """
        Get all reflections for a specific trade.
        
        Args:
            trade_id: Trade identifier
            
        Returns:
            List of Reflection objects
        """
        session = self._get_session()
        try:
            records = (
                session.query(ReflectionRecord)
                .filter_by(trade_id=trade_id)
                .order_by(ReflectionRecord.created_at.desc())
                .all()
            )
            
            # Get trade outcome
            trade = self.get_trade(trade_id)
            if not trade:
                return []
            
            return [
                Reflection(
                    trade_id=record.trade_id,
                    trade_outcome=trade,
                    accuracy_assessment=record.accuracy_assessment,
                    key_learnings=record.key_learnings or [],
                    belief_adjustments=record.belief_adjustments or [],
                    actionable_improvements=record.actionable_improvements or [],
                    timestamp=record.created_at,
                )
                for record in records
            ]
        finally:
            session.close()
    
    def get_performance_statistics(self) -> Dict[str, Any]:
        """
        Get overall performance statistics.
        
        Returns:
            Dictionary with performance metrics
        """
        session = self._get_session()
        try:
            total_trades = session.query(TradeRecord).count()
            closed_trades = session.query(TradeRecord).filter(
                TradeRecord.outcome_status.in_(["closed_profit", "closed_loss", "stopped_out"])
            ).all()
            
            if not closed_trades:
                return {
                    "total_trades": total_trades,
                    "closed_trades": 0,
                    "win_rate": 0.0,
                    "avg_pnl": 0.0,
                    "total_pnl": 0.0,
                }
            
            profitable_trades = [t for t in closed_trades if t.pnl and t.pnl > 0]
            total_pnl = sum(t.pnl for t in closed_trades if t.pnl)
            avg_pnl = total_pnl / len(closed_trades) if closed_trades else 0.0
            
            return {
                "total_trades": total_trades,
                "closed_trades": len(closed_trades),
                "win_rate": len(profitable_trades) / len(closed_trades) if closed_trades else 0.0,
                "avg_pnl": avg_pnl,
                "total_pnl": total_pnl,
            }
        finally:
            session.close()
    
    def __repr__(self) -> str:
        stats = self.get_performance_statistics()
        return f"EpisodicMemory(trades={stats['total_trades']}, win_rate={stats['win_rate']:.2%})"
