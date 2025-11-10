Project Shri Sudarshan: A Hybrid Multi-Agent LLM Architecture for Stock and Derivatives Trading

![Test](https://github.com/s-p-c-git/ShriSudarshan/workflows/Test/badge.svg)
![Lint](https://github.com/s-p-c-git/ShriSudarshan/workflows/Lint/badge.svg)
![Build](https://github.com/s-p-c-git/ShriSudarshan/workflows/Build/badge.svg)
![Security](https://github.com/s-p-c-git/ShriSudarshan/workflows/Security/badge.svg)

1. Overview
This document outlines the architecture and development plan for "Project Shri Sudarshan," a sophisticated, LLM-based multi-agent system for trading stocks and Futures & Options (FnO). The primary objective of this system is to maximize profit through a robust, collaborative, and self-improving decision-making process that embodies precision, protection, and divine vision.
The design is a hybrid model that synthesizes the most effective concepts from our comprehensive research, primarily contrasting and combining the strengths of:
 * FinCon: A hierarchical, two-tier system with strong risk control and advanced learning mechanisms, as detailed in the MQL5 article (https://www.mql5.com/en/articles/16916).
 * TradingAgents: An open-source, collaborative framework that emulates a real-world trading firm with specialized teams and a unique "debate" mechanism to reduce bias.
The Shri Sudarshan architecture adopts the comprehensive, team-based structure of TradingAgents as its foundation while integrating the sophisticated risk management and reflective learning loops of FinCon to create a system that is both dynamic in its analysis and resilient in its operation.
2. Proposed Architecture: System Blueprint
Project Shri Sudarshan is designed as a modular, hierarchical system where teams of specialized LLM-powered agents collaborate to generate, scrutinize, and execute trading strategies.
 * Orchestration Framework: The system will be orchestrated using LangGraph. This framework is chosen for its proven effectiveness in managing stateful, multi-agent workflows in similar projects like TradingAgents and PrimoAgent.
Agent Teams and Roles
The system is organized into four distinct, collaborative teams:
a) Market Intelligence Team (The Analysts)
This team is responsible for multi-modal data ingestion and initial analysis, mirroring the structure of the analyst team in TradingAgents.
 * Fundamentals Analyst: Scours financial reports (10-Ks, 10-Qs), earnings call transcripts, and balance sheets to determine the intrinsic value of assets.
 * Macro & News Analyst: Monitors macroeconomic data, central bank policies, geopolitical events, and breaking news to provide a top-down market view.
 * Sentiment Analyst: Gauges market mood by analyzing social media, forums, and news sentiment trends.
 * Technical Analyst: Analyzes price charts and volume data for stocks and their underlying assets to identify patterns, trends, and key support/resistance levels.
 * **FinBERT Sentiment Analyst** (NEW): Uses the specialized FinBERT model for high-speed, quantitative sentiment analysis of financial news and text, providing precise sentiment scores (-1 to +1).
 * **FinGPT Generative Analyst** (NEW): Employs FinGPT for deep qualitative analysis, generating insights, risk assessments, and opportunities from financial documents and news.
b) Strategy & Research Team (The Debaters)
This is the core reasoning hub where initial analyses are challenged and refined into actionable strategies. It expands on the TradingAgents researcher team concept.
 * Bullish Researcher: Constructs the strongest possible argument for taking long positions or implementing bullish strategies based on the analysts' reports.
 * Bearish Researcher: Acts as the adversary, focusing on risks, potential downsides, and constructing the strongest case for shorting or bearish strategies.
 * Derivatives Strategist (FnO Specialist): A critical addition for FnO trading. This agent analyzes implied vs. historical volatility, options greeks (Delta, Vega, Theta), and term structure. Based on the outcome of the bull/bear debate, it proposes specific FnO strategies (e.g., covered calls, protective puts, volatility plays like straddles) that align with the firm's market outlook.
c) Execution Team (The Traders)
This team is responsible for the practical implementation of the approved strategies.
 * Equity Trader: Focuses on optimal execution for stock trades, determining the best order types, timing, and sizing to minimize slippage and market impact.
 * FnO Trader: A specialized agent responsible for executing complex, multi-leg options and futures strategies, managing the order book for less liquid options, and monitoring positions near expiry.
d) Oversight & Learning Team (The Management)
This team provides top-level control, risk management, and facilitates system-wide learning, directly incorporating the principles of FinCon's two-tier hierarchy and advanced learning mechanisms.
 * Portfolio Manager: The central decision-making agent, analogous to FinCon's Manager. It receives the final, debated strategy proposal and makes the ultimate decision to approve or reject a trade.
 * Risk Manager: Operates as an independent oversight layer. It assesses the impact of any proposed trade on the overall portfolio's risk exposure (e.g., VaR, sector concentration). It has the authority to veto trades that violate predefined risk parameters, providing the robust risk control seen in FinCon.
 * Reflective Agent: This agent embodies FinCon's Conceptual Verbal Reinforcement (CVRF) and episodic memory concepts. It performs post-trade analysis by reviewing the outcomes of past decisions to generate "conceptual recommendations for belief adjustment." These insights are fed back to the Portfolio Manager to refine high-level strategy over time.
3. Information Flow & Decision-Making Logic
The system operates in a structured, sequential workflow managed by LangGraph to ensure every decision is thoroughly vetted.
 * Analysis Phase: The Market Intelligence Team agents run concurrently, each producing a structured report on their domain.
 * Debate & Strategy Phase: These reports are fed into the Strategy & Research Team. The Bullish and Bearish agents engage in a structured, multi-round debate. The Derivatives Strategist observes and formulates specific FnO strategies based on the consensus.
 * Proposal Phase: A consolidated packet containing the analyst reports, the full debate transcript, and a final strategy proposal is passed to the Execution Team.
 * Execution Planning: The relevant Trader agents create a detailed execution plan, specifying order types, limits, and timing.
 * Approval Phase: The complete proposal is submitted to the Oversight Team. The Risk Manager runs a compliance check. If it passes, the Portfolio Manager gives the final approval.
 * Execution Phase: Upon approval, the Trader agents execute the orders via broker APIs.
 * Learning Loop: The trade's outcome is logged in the system's "episodic memory." The Reflective Agent periodically analyzes these logs to generate strategic feedback, completing the learning cycle.
4. Development Plan & Technology Stack
 * Core Framework: LangGraph for orchestrating agent teams and managing complex state transitions.
 * LLMs: A dual-model approach is optimal. The system supports multiple LLM providers:
   * **OpenAI**: Use faster, cost-effective models (e.g., gpt-4o-mini) for routine data processing and more powerful models (e.g., gpt-4o) for critical debate, strategy, and management functions.
   * **Anthropic**: Use Claude 3.5 Sonnet for both routine and critical tasks. Claude offers competitive performance with different pricing and capabilities.
   * The system allows flexible provider selection via configuration, enabling users to choose based on cost, performance, or API availability.
 * Data Feeds:
   * Stocks: Standard providers like Alpha Vantage or yfinance for pricing, fundamentals, and news.
   * FnO: A specialized data provider is required for real-time options chain data, implied volatility surfaces, and greeks.
 * Memory Module: Develop an explicit, layered memory system inspired by FinCon and FinMem. This will involve using vector databases to store and retrieve information for:
   * Working Memory: Short-term state for ongoing analysis.
   * Procedural Memory: Successful sub-tasks and analytical workflows.
   * Episodic Memory: Long-term storage of past trades and their rationales for the Reflective Agent.
 * Backtesting Environment: A high-fidelity, event-driven backtesting simulator is crucial. It must be capable of handling the complexities of both stock and FnO trading, including order book dynamics, slippage, commissions, and options-specific events like expiry and assignment.
5. Getting Started
Prerequisites
 * Python 3.9+
 * An LLM provider API key:
   * **OpenAI API key** (for GPT-4o, GPT-4o-mini), OR
   * **Anthropic API key** (for Claude 3.5 Sonnet)
 * API keys for your chosen data vendors (e.g., Alpha Vantage)
 * **PyTorch and Transformers** (for FinBERT and FinGPT agents)
Installation
 * Clone the repository:
   git clone https://github.com/s-p-c-git/ShriSudarshan.git
   cd ShriSudarshan

 * Install dependencies:
   pip install -r requirements.txt

   Note: This includes transformers, torch, and other dependencies needed for FinBERT and FinGPT integration.

 * Configure your API keys:
   * Rename .env.example to .env.
   * Add your LLM provider API key(s) to the .env file:
     * For **OpenAI**: Set `OPENAI_API_KEY` and `LLM_PROVIDER=openai` (default)
     * For **Anthropic**: Set `ANTHROPIC_API_KEY` and `LLM_PROVIDER=anthropic`
   * Add your data provider API keys (e.g., Alpha Vantage)

LLM Provider Configuration
The system supports multiple LLM providers with flexible configuration:

**Using OpenAI (Default)**:
```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=your_openai_api_key_here
PREMIUM_MODEL=gpt-4o
STANDARD_MODEL=gpt-4o-mini
```

**Using Anthropic Claude**:
```bash
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=your_anthropic_api_key_here
ANTHROPIC_PREMIUM_MODEL=claude-3-5-sonnet-20241022
ANTHROPIC_STANDARD_MODEL=claude-3-5-sonnet-20241022
```

**Mixed Mode**: You can also use different providers for different agents by specifying the provider when initializing agents in code.

Running the System
   cd src
   python main.py --symbol AAPL --start_date 2023-01-01 --end_date 2023-01-31

Docker Installation (Alternative)
For containerized deployment, you can use Docker:
 * Quick start with Docker Compose:
   docker-compose up -d
   docker-compose run --rm shri-sudarshan --symbol AAPL

 * Or build and run manually:
   docker build -t shri-sudarshan:latest .
   docker run --rm --env-file .env -v $(pwd)/data:/app/data shri-sudarshan:latest --symbol AAPL

 * For GPU support (FinBERT/FinGPT acceleration):
   docker build -f Dockerfile.gpu -t shri-sudarshan:gpu .
   docker run --gpus all --rm --env-file .env -v $(pwd)/data:/app/data shri-sudarshan:gpu --symbol AAPL

See DOCKER.md for complete Docker documentation including:
 * Detailed setup and configuration
 * Volume management and data persistence
 * Production deployment guidelines
 * GPU support instructions
 * Troubleshooting guide

6. Project Documentation
The project includes comprehensive documentation:

Core Documentation:
 * APPROACH.md - Detailed approach document with prerequisites, requirements analysis, and implementation plan
 * IMPLEMENTATION_SUMMARY.md - Complete summary of what has been implemented
 * docs/architecture.md - System architecture and design details
 * docs/getting_started.md - Step-by-step installation and usage guide

Agent Documentation:
 * docs/AGENT_BEHAVIORS.md - Complete guide to agent behaviors, decision logic, and interactions
 * docs/SYSTEM_PROMPTS.md - System prompts for all 11 agents with customization guidance

Technical Documentation:
 * docs/API_REFERENCE.md - Complete API reference with practical examples
 * docs/DEPLOYMENT.md - Deployment guide for Docker, Kubernetes, and cloud platforms
 * docs/TESTING.md - Testing strategies and best practices
 * docs/INTEGRATION_TESTING.md - Guide for running integration tests with Anthropic API

Operations Documentation:
 * docs/TROUBLESHOOTING.md - Common issues and solutions
 * docs/CONTRIBUTING.md - Contribution guidelines and development workflow

Examples:
 * examples/simple_analysis.py - Basic workflow usage example
 * examples/advanced_usage.py - Custom agents and workflow customization
 * examples/batch_analysis.py - Batch processing and reporting

7. Project Status
Phase 1 Implementation: COMPLETE ✅
 * Project structure established
 * Configuration management system
 * Base agent framework
 * Memory system (working, procedural, episodic)
 * LangGraph orchestration workflow
 * CLI interface
 * Comprehensive documentation

Phase 2 Development: IN PROGRESS 🚧
 * Individual agent implementations
 * Data provider integrations
 * Debate mechanism
 * Risk calculations
 * Testing framework

8. Architecture Overview
The system consists of:
 * 11 specialized LLM agents across 4 teams
 * 3-layer memory system (working, procedural, episodic)
 * LangGraph-based orchestration
 * Multi-phase workflow with approval gates
 * Risk management and learning loops

For detailed architecture information, see docs/architecture.md.

9. Contributing

**⚠️ Important: All code must be formatted with Black and Ruff before committing!**

We welcome contributions! Before you start:

1. **Set up pre-commit hooks (REQUIRED)**:
   ```bash
   pip install black ruff mypy pre-commit
   pre-commit install
   ```

2. **Format your code**:
   ```bash
   black src/ tests/ examples/
   ruff check --fix src/ tests/ examples/
   ```

3. **Run tests**:
   ```bash
   pytest tests/
   ```

**Pre-commit hooks will automatically format your code on every commit. CI/CD will block PRs that don't pass formatting checks.**

For detailed contributing guidelines, see [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md).

Quick reference:
- Setup and workflow: [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md)
- Coding standards: [.github/copilot-instructions.md](.github/copilot-instructions.md)
- Testing guide: [docs/TESTING.md](docs/TESTING.md)

