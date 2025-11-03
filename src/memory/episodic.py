"""
Episodic Memory module for Project Shri Sudarshan.

Episodic memory stores historical trades and their outcomes
for learning and reflection.
"""

from datetime import datetime
from typing import Any, Optional

from sqlalchemy import JSON, Column, DateTime, Float, String, Text, create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from ..config import settings
from ..data.schemas import Reflection, TradeOutcome


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
    quantity = Column(Float, nullable=False)
    realized_pnl = Column(Float)
    return_pct = Column(Float)
    outcome = Column(String, nullable=False, default="pending")
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.now)


class ReflectionRecord(Base):
    """Database model for reflection records."""

    __tablename__ = "reflections"

    reflection_id = Column(String, primary_key=True)
    trade_id = Column(String, nullable=False)
    symbol = Column(String, nullable=False)
    analysis_summary = Column(Text, nullable=False)
    what_worked = Column(JSON)
    what_failed = Column(JSON)
    lessons_learned = Column(JSON)
    strategic_recommendations = Column(JSON)
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
            # Handle both string and enum types for strategy_type
            # Pydantic's use_enum_values=True converts enums to strings
            strategy_type_value = (
                trade.strategy_type
                if isinstance(trade.strategy_type, str)
                else trade.strategy_type.value
            )

            record = TradeRecord(
                trade_id=trade.trade_id,
                symbol=trade.symbol,
                strategy_type=strategy_type_value,
                entry_date=trade.entry_date,
                exit_date=trade.exit_date,
                entry_price=trade.entry_price,
                exit_price=trade.exit_price,
                quantity=trade.quantity,
                realized_pnl=trade.realized_pnl,
                return_pct=trade.return_pct,
                outcome=trade.outcome,
                notes=trade.notes,
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
                reflection_id=f"refl_{reflection.trade_id}_{int(datetime.now().timestamp() * 1000000)}",
                trade_id=reflection.trade_id,
                symbol=reflection.symbol,
                analysis_summary=reflection.analysis_summary,
                what_worked=reflection.what_worked,
                what_failed=reflection.what_failed,
                lessons_learned=reflection.lessons_learned,
                strategic_recommendations=reflection.strategic_recommendations,
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

            from ..data.schemas import StrategyType

            return TradeOutcome(
                trade_id=record.trade_id,
                symbol=record.symbol,
                strategy_type=StrategyType(record.strategy_type),
                entry_date=record.entry_date,
                exit_date=record.exit_date,
                entry_price=record.entry_price,
                exit_price=record.exit_price,
                quantity=record.quantity,
                realized_pnl=record.realized_pnl,
                return_pct=record.return_pct,
                outcome=record.outcome,
                notes=record.notes or "",
            )
        finally:
            session.close()

    def get_trades_by_symbol(self, symbol: str, limit: int = 10) -> list[TradeOutcome]:
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

            from ..data.schemas import StrategyType

            return [
                TradeOutcome(
                    trade_id=record.trade_id,
                    symbol=record.symbol,
                    strategy_type=StrategyType(record.strategy_type),
                    entry_date=record.entry_date,
                    exit_date=record.exit_date,
                    entry_price=record.entry_price,
                    exit_price=record.exit_price,
                    quantity=record.quantity,
                    realized_pnl=record.realized_pnl,
                    return_pct=record.return_pct,
                    outcome=record.outcome,
                    notes=record.notes or "",
                )
                for record in records
            ]
        finally:
            session.close()

    def get_reflections_for_trade(self, trade_id: str) -> list[Reflection]:
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

            return [
                Reflection(
                    trade_id=record.trade_id,
                    symbol=record.symbol,
                    analysis_summary=record.analysis_summary,
                    what_worked=record.what_worked or [],
                    what_failed=record.what_failed or [],
                    lessons_learned=record.lessons_learned or [],
                    strategic_recommendations=record.strategic_recommendations or [],
                    timestamp=record.created_at,
                )
                for record in records
            ]
        finally:
            session.close()

    def get_performance_statistics(self) -> dict[str, Any]:
        """
        Get overall performance statistics.

        Returns:
            Dictionary with performance metrics
        """
        session = self._get_session()
        try:
            total_trades = session.query(TradeRecord).count()
            closed_trades = (
                session.query(TradeRecord)
                .filter(TradeRecord.outcome.in_(["win", "loss", "breakeven"]))
                .all()
            )

            if not closed_trades:
                return {
                    "total_trades": total_trades,
                    "closed_trades": 0,
                    "win_rate": 0.0,
                    "avg_pnl": 0.0,
                    "total_pnl": 0.0,
                }

            profitable_trades = [t for t in closed_trades if t.realized_pnl and t.realized_pnl > 0]
            total_pnl = sum(t.realized_pnl for t in closed_trades if t.realized_pnl)
            avg_pnl = total_pnl / len(closed_trades) if closed_trades else 0.0

            return {
                "total_trades": total_trades,
                "closed_trades": len(closed_trades),
                "win_rate": (len(profitable_trades) / len(closed_trades) if closed_trades else 0.0),
                "avg_pnl": avg_pnl,
                "total_pnl": total_pnl,
            }
        finally:
            session.close()

    def __repr__(self) -> str:
        stats = self.get_performance_statistics()
        return f"EpisodicMemory(trades={stats['total_trades']}, win_rate={stats['win_rate']:.2%})"
