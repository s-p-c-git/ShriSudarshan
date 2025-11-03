"""Unit tests for orchestration state module."""

from datetime import datetime

from src.orchestration.state import create_initial_state


class TestTradingSystemState:
    """Test suite for TradingSystemState."""

    def test_create_initial_state_minimal(self):
        """Test creating initial state with minimal parameters."""
        state = create_initial_state("AAPL")

        assert state["symbol"] == "AAPL"
        assert state["start_date"] is None
        assert state["end_date"] is None
        assert state["current_phase"] == "initialization"
        assert isinstance(state["workflow_start_time"], datetime)

    def test_create_initial_state_with_dates(self):
        """Test creating initial state with date range."""
        state = create_initial_state("AAPL", start_date="2024-01-01", end_date="2024-01-31")

        assert state["symbol"] == "AAPL"
        assert state["start_date"] == "2024-01-01"
        assert state["end_date"] == "2024-01-31"

    def test_initial_state_analysis_phase(self):
        """Test initial state for analysis phase."""
        state = create_initial_state("AAPL")

        assert state["analyst_reports"] == {}
        assert state["analysis_complete"] is False

    def test_initial_state_debate_phase(self):
        """Test initial state for debate phase."""
        state = create_initial_state("AAPL")

        assert state["debate_arguments"] == []
        assert state["debate_rounds"] == 0
        assert state["debate_complete"] is False

    def test_initial_state_strategy_phase(self):
        """Test initial state for strategy phase."""
        state = create_initial_state("AAPL")

        assert state["strategy_proposal"] is None
        assert state["strategy_complete"] is False

    def test_initial_state_execution_planning_phase(self):
        """Test initial state for execution planning phase."""
        state = create_initial_state("AAPL")

        assert state["execution_plan"] is None
        assert state["execution_plan_complete"] is False

    def test_initial_state_risk_assessment_phase(self):
        """Test initial state for risk assessment phase."""
        state = create_initial_state("AAPL")

        assert state["risk_assessment"] is None
        assert state["risk_approved"] is False

    def test_initial_state_portfolio_decision_phase(self):
        """Test initial state for portfolio decision phase."""
        state = create_initial_state("AAPL")

        assert state["portfolio_decision"] is None
        assert state["final_approval"] is False

    def test_initial_state_execution_phase(self):
        """Test initial state for execution phase."""
        state = create_initial_state("AAPL")

        assert state["orders_submitted"] is False
        assert state["execution_complete"] is False

    def test_initial_state_errors(self):
        """Test initial state has empty errors list."""
        state = create_initial_state("AAPL")

        assert state["errors"] == []

    def test_state_mutability(self):
        """Test that state can be modified."""
        state = create_initial_state("AAPL")

        # Modify state
        state["current_phase"] = "analysis"
        state["analysis_complete"] = True
        state["errors"].append("Test error")

        assert state["current_phase"] == "analysis"
        assert state["analysis_complete"] is True
        assert len(state["errors"]) == 1

    def test_state_with_analyst_reports(self, sample_fundamentals_report):
        """Test state with analyst reports."""
        state = create_initial_state("AAPL")

        state["analyst_reports"] = {"fundamentals": sample_fundamentals_report}

        assert "fundamentals" in state["analyst_reports"]
        assert state["analyst_reports"]["fundamentals"].symbol == "AAPL"

    def test_state_with_debate_arguments(self, sample_debate_arguments):
        """Test state with debate arguments."""
        state = create_initial_state("AAPL")

        state["debate_arguments"] = sample_debate_arguments
        state["debate_rounds"] = 1
        state["debate_complete"] = True

        assert len(state["debate_arguments"]) == 2
        assert state["debate_rounds"] == 1
        assert state["debate_complete"] is True

    def test_state_with_strategy_proposal(self, sample_strategy_proposal):
        """Test state with strategy proposal."""
        state = create_initial_state("AAPL")

        state["strategy_proposal"] = sample_strategy_proposal
        state["strategy_complete"] = True

        assert state["strategy_proposal"] is not None
        assert state["strategy_complete"] is True

    def test_state_with_execution_plan(self, sample_execution_plan):
        """Test state with execution plan."""
        state = create_initial_state("AAPL")

        state["execution_plan"] = sample_execution_plan
        state["execution_plan_complete"] = True

        assert state["execution_plan"] is not None
        assert state["execution_plan_complete"] is True

    def test_state_with_risk_assessment(self, sample_risk_assessment):
        """Test state with risk assessment."""
        state = create_initial_state("AAPL")

        state["risk_assessment"] = sample_risk_assessment
        state["risk_approved"] = sample_risk_assessment.approved

        assert state["risk_assessment"] is not None
        assert state["risk_approved"] is True

    def test_state_with_portfolio_decision(self, sample_portfolio_decision):
        """Test state with portfolio decision."""
        state = create_initial_state("AAPL")

        state["portfolio_decision"] = sample_portfolio_decision
        state["final_approval"] = sample_portfolio_decision.approved

        assert state["portfolio_decision"] is not None
        assert state["final_approval"] is True

    def test_state_workflow_progression(self):
        """Test state progression through workflow phases."""
        state = create_initial_state("AAPL")

        # Track phases
        phases = []

        # Analysis
        state["current_phase"] = "analysis"
        state["analysis_complete"] = True
        phases.append(state["current_phase"])

        # Debate
        state["current_phase"] = "debate"
        state["debate_complete"] = True
        phases.append(state["current_phase"])

        # Strategy
        state["current_phase"] = "strategy"
        state["strategy_complete"] = True
        phases.append(state["current_phase"])

        # Execution planning
        state["current_phase"] = "execution_planning"
        state["execution_plan_complete"] = True
        phases.append(state["current_phase"])

        # Risk assessment
        state["current_phase"] = "risk_assessment"
        state["risk_approved"] = True
        phases.append(state["current_phase"])

        # Portfolio decision
        state["current_phase"] = "portfolio_decision"
        state["final_approval"] = True
        phases.append(state["current_phase"])

        # Execution
        state["current_phase"] = "execution"
        state["execution_complete"] = True
        phases.append(state["current_phase"])

        # Verify progression
        assert len(phases) == 7
        assert phases[-1] == "execution"
        assert state["execution_complete"] is True

    def test_state_error_tracking(self):
        """Test error tracking in state."""
        state = create_initial_state("AAPL")

        # Add multiple errors
        state["errors"].append("Analysis failed")
        state["errors"].append("Debate failed")
        state["errors"].append("Strategy failed")

        assert len(state["errors"]) == 3
        assert "Analysis failed" in state["errors"]
        assert "Debate failed" in state["errors"]
        assert "Strategy failed" in state["errors"]

    def test_state_multiple_symbols(self):
        """Test creating states for multiple symbols."""
        symbols = ["AAPL", "MSFT", "GOOGL"]
        states = [create_initial_state(symbol) for symbol in symbols]

        assert len(states) == 3
        assert states[0]["symbol"] == "AAPL"
        assert states[1]["symbol"] == "MSFT"
        assert states[2]["symbol"] == "GOOGL"

        # Each should have independent errors list
        states[0]["errors"].append("Error 1")
        states[1]["errors"].append("Error 2")

        assert len(states[0]["errors"]) == 1
        assert len(states[1]["errors"]) == 1
        assert states[0]["errors"][0] != states[1]["errors"][0]


class TestStateTransitions:
    """Test state transition logic."""

    def test_analysis_to_debate_transition(self, sample_analyst_reports):
        """Test transition from analysis to debate phase."""
        state = create_initial_state("AAPL")

        # Complete analysis phase
        state["analyst_reports"] = sample_analyst_reports
        state["analysis_complete"] = True
        state["current_phase"] = "analysis"

        # Transition to debate
        state["current_phase"] = "debate"

        assert state["analysis_complete"] is True
        assert state["current_phase"] == "debate"
        assert len(state["analyst_reports"]) > 0

    def test_debate_to_strategy_transition(self, sample_debate_arguments):
        """Test transition from debate to strategy phase."""
        state = create_initial_state("AAPL")

        # Complete debate phase
        state["debate_arguments"] = sample_debate_arguments
        state["debate_complete"] = True
        state["current_phase"] = "debate"

        # Transition to strategy
        state["current_phase"] = "strategy"

        assert state["debate_complete"] is True
        assert state["current_phase"] == "strategy"
        assert len(state["debate_arguments"]) > 0

    def test_risk_rejection_flow(self, sample_risk_assessment):
        """Test workflow when risk assessment rejects."""
        state = create_initial_state("AAPL")

        # Risk assessment rejects
        sample_risk_assessment.approved = False
        state["risk_assessment"] = sample_risk_assessment
        state["risk_approved"] = False
        state["current_phase"] = "risk_assessment"

        # Should not proceed to portfolio decision
        assert state["risk_approved"] is False
        assert state["portfolio_decision"] is None
        assert state["final_approval"] is False

    def test_portfolio_rejection_flow(self, sample_portfolio_decision):
        """Test workflow when portfolio manager rejects."""
        state = create_initial_state("AAPL")

        # Portfolio manager rejects
        sample_portfolio_decision.approved = False
        state["portfolio_decision"] = sample_portfolio_decision
        state["final_approval"] = False
        state["current_phase"] = "portfolio_decision"

        # Should not proceed to execution
        assert state["final_approval"] is False
        assert state["orders_submitted"] is False
        assert state["execution_complete"] is False
