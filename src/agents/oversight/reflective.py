"""Oversight & Learning Team - Reflective Agent."""

from typing import Any, Dict

from ..base import CriticalAgent
from ...config.prompts import REFLECTIVE_AGENT_PROMPT
from ...data.schemas import AgentRole, Reflection, TradeOutcome
from ...memory import EpisodicMemory
from ...utils import get_logger

logger = get_logger(__name__)


class ReflectiveAgent(CriticalAgent):
    """
    Reflective Agent.
    
    Performs post-trade analysis to generate learning insights.
    Embodies Conceptual Verbal Reinforcement (CVRF) for system improvement.
    """
    
    def __init__(self):
        super().__init__(
            role=AgentRole.REFLECTIVE_AGENT,
            system_prompt=REFLECTIVE_AGENT_PROMPT,
            temperature=0.6,
        )
        self.episodic_memory = EpisodicMemory()
    
    async def reflect_on_trade(self, context: Dict[str, Any]) -> Reflection:
        """
        Analyze trade outcome and generate learning insights.
        
        Args:
            context: Contains trade_outcome, original_rationale, etc.
            
        Returns:
            Reflection with learning insights
        """
        trade_outcome: TradeOutcome = context.get("trade_outcome")
        
        if not trade_outcome:
            logger.warning("No trade outcome provided for reflection")
            return None
        
        logger.info("Reflecting on trade", trade_id=trade_outcome.trade_id)
        
        try:
            # Determine if trade was successful
            if trade_outcome.return_pct:
                success = trade_outcome.return_pct > 0
            else:
                success = False
            
            # Store trade outcome in episodic memory
            self.episodic_memory.store_trade(trade_outcome)
            
            # Simple reflection for now
            # In production, would use LLM to generate deeper insights
            
            if success:
                what_worked = ["Strategy execution was successful"]
                what_failed = []
                adjustments = ["Continue monitoring similar opportunities"]
            else:
                what_worked = []
                what_failed = ["Strategy did not achieve expected returns"]
                adjustments = ["Review entry/exit conditions", "Re-evaluate confidence scoring"]
            
            reflection = Reflection(
                trade_id=trade_outcome.trade_id,
                symbol=trade_outcome.symbol,
                outcome_summary=f"Trade {'succeeded' if success else 'failed'} with {trade_outcome.return_pct or 0:.1f}% return",
                what_worked=what_worked,
                what_failed=what_failed,
                market_lessons=["Market conditions evolved as expected" if success else "Market behaved differently than anticipated"],
                strategic_adjustments=adjustments,
                confidence_impact="Maintain confidence" if success else "Reduce confidence in similar setups",
                conceptual_recommendations="System operating as expected" if success else "Review decision-making process",
            )
            
            # Store reflection
            self.episodic_memory.store_reflection(reflection)
            
            logger.info(
                "Reflection complete",
                trade_id=trade_outcome.trade_id,
                success=success,
            )
            
            return reflection
            
        except Exception as e:
            logger.error("Reflection failed", trade_id=trade_outcome.trade_id if trade_outcome else "unknown", error=str(e))
            return None
