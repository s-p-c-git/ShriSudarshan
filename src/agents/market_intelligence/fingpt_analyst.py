"""Market Intelligence Team - FinGPT Generative Analyst.

This module provides in-depth generative analysis using FinGPT for
financial text summarization and insights.
"""

from typing import Any, Optional

from ...data.schemas import AgentRole, FinGPTGenerativeReport
from ...utils import get_logger


logger = get_logger(__name__)

# Configuration constants
MAX_INPUT_LENGTH = 2000  # Maximum input text length to avoid token limits
MIN_INSIGHTS_FOR_HIGH_CONFIDENCE = 3  # Minimum insights for confidence >= 0.8
MIN_RISKS_FOR_HIGH_CONFIDENCE = 2  # Minimum risks for confidence >= 0.9
MIN_OPPORTUNITIES_FOR_HIGH_CONFIDENCE = 2  # Minimum opportunities for confidence >= 0.9
BASE_CONFIDENCE = 0.7  # Default confidence level
HIGH_CONFIDENCE_THRESHOLD = 0.8  # Confidence with good insights
VERY_HIGH_CONFIDENCE_THRESHOLD = 0.9  # Confidence with insights, risks, and opportunities


class FinGPTGenerativeAnalyst:
    """
    FinGPT Generative Analyst agent.

    Uses FinGPT (or similar generative financial LLM) for deep qualitative
    analysis including summarization, question-answering, and recommendations.
    """

    def __init__(self, model_name: Optional[str] = None, use_local: bool = True):
        """
        Initialize the FinGPT Generative Analyst.

        Args:
            model_name: Model name/path for FinGPT (e.g., 'FinGPT/fingpt-forecaster_dow30_llama2-7b_lora')
            use_local: If True, use local model; if False, use API endpoint
        """
        self.role = AgentRole.FINGPT_GENERATIVE_ANALYST
        self.model_name = model_name or "FinGPT/fingpt-forecaster_dow30_llama2-7b_lora"
        self.use_local = use_local
        self._model = None
        self._tokenizer = None

        # Define task-specific prompts
        self.prompts = {
            "summarize_filing": """Analyze the following financial filing excerpt and provide:
1. Key financial metrics and their implications
2. Major risks identified
3. Strategic opportunities
4. Overall assessment

Text: {text}

Provide a structured summary focusing on investment implications.""",
            "analyze_transcript": """Analyze the following earnings call transcript excerpt:
1. Management sentiment and confidence
2. Key forward-looking statements
3. Concerns raised by analysts
4. Strategic initiatives discussed

Transcript: {text}

Summarize the investment-relevant insights.""",
            "analyze_news": """Analyze the following news articles for {symbol}:
1. Key themes and trends
2. Potential market impact
3. Short-term vs long-term implications
4. Sentiment and positioning recommendations

News: {text}

Provide actionable insights for trading decisions.""",
            "general_analysis": """Analyze the following financial information for {symbol}:

{text}

Provide:
1. Key insights relevant to investment decisions
2. Identified risks
3. Identified opportunities
4. Overall recommendation or summary
""",
        }

    def _load_model(self):
        """Lazy load the FinGPT model and tokenizer."""
        if self._model is None and self.use_local:
            try:
                from transformers import AutoModelForCausalLM, AutoTokenizer

                logger.info("Loading FinGPT model", model=self.model_name)
                self._tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                self._model = AutoModelForCausalLM.from_pretrained(
                    self.model_name, device_map="auto", load_in_8bit=True
                )
                logger.info("FinGPT model loaded successfully")
            except ImportError as e:
                logger.error(
                    "Failed to import transformers. Install with: pip install transformers torch"
                )
                raise ImportError(
                    "transformers library required for FinGPT. "
                    "Install with: pip install transformers torch bitsandbytes accelerate"
                ) from e
            except Exception as e:
                logger.error("Failed to load FinGPT model", error=str(e))
                raise

    def _generate_response(self, prompt: str, max_length: int = 512) -> str:
        """
        Generate a response using FinGPT.

        Args:
            prompt: Input prompt
            max_length: Maximum length of generated text

        Returns:
            Generated text response
        """
        if not self.use_local:
            # Placeholder for API-based generation
            logger.warning("API-based FinGPT not implemented, returning placeholder")
            return (
                "FinGPT analysis placeholder. Configure API endpoint or use local model."
            )

        self._load_model()

        # Ensure model is loaded before accessing its device
        if self._model is None:
            logger.error("FinGPT local model could not be loaded. Returning placeholder response.")
            return (
                "FinGPT analysis unavailable: local model could not be loaded. "
                "Check model path or configuration."
            )
        # Tokenize input
        inputs = self._tokenizer(prompt, return_tensors="pt").to(self._model.device)

        # Generate response
        outputs = self._model.generate(
            **inputs,
            max_length=max_length,
            num_return_sequences=1,
            temperature=0.7,
            top_p=0.9,
            do_sample=True,
        )

        # Decode response
        response = self._tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Remove the input prompt from response
        if prompt in response:
            response = response.replace(prompt, "").strip()

        return response

    def _parse_analysis(self, response: str) -> dict[str, Any]:
        """
        Parse the generated analysis into structured format.

        Args:
            response: Generated text from FinGPT

        Returns:
            Structured analysis dict
        """
        # Simple parsing - look for numbered lists or bullet points
        insights = []
        risks = []
        opportunities = []

        lines = response.split("\n")
        current_section = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Detect sections
            lower_line = line.lower()
            if "insight" in lower_line or "key" in lower_line:
                current_section = "insights"
                continue
            elif "risk" in lower_line or "concern" in lower_line:
                current_section = "risks"
                continue
            elif "opportunit" in lower_line or "potential" in lower_line:
                current_section = "opportunities"
                continue

            # Add to appropriate list
            if line.startswith(("- ", "* ", "• ")) or (line and line[0].isdigit()):
                clean_line = line.lstrip("-*•0123456789. ").strip()
                if current_section == "insights":
                    insights.append(clean_line)
                elif current_section == "risks":
                    risks.append(clean_line)
                elif current_section == "opportunities":
                    opportunities.append(clean_line)
                else:
                    # Default to insights if no section detected
                    insights.append(clean_line)

        return {
            "insights": insights[:5],  # Top 5
            "risks": risks[:3],  # Top 3
            "opportunities": opportunities[:3],  # Top 3
        }

    async def analyze(self, context: dict[str, Any]) -> FinGPTGenerativeReport:
        """
        Perform generative analysis using FinGPT.

        Args:
            context: Contains 'symbol', 'texts' or 'text', 'analysis_type' (optional)

        Returns:
            FinGPTGenerativeReport with generative analysis
        """
        symbol = context.get("symbol", "UNKNOWN")
        text = context.get("text", "")
        texts = context.get("texts", [])
        analysis_type = context.get("analysis_type", "general_analysis")

        # Combine texts if multiple provided
        if texts and not text:
            text = "\n\n".join(texts[:3])  # Use first 3 texts to avoid token limits

        logger.info(
            "Starting FinGPT generative analysis",
            symbol=symbol,
            analysis_type=analysis_type,
        )

        try:
            # Select appropriate prompt
            prompt_template = self.prompts.get(analysis_type, self.prompts["general_analysis"])
            prompt = prompt_template.format(symbol=symbol, text=text[:MAX_INPUT_LENGTH])

            # Generate analysis
            response = self._generate_response(prompt, max_length=512)

            # Parse structured data
            parsed = self._parse_analysis(response)

            # Calculate confidence based on response quality
            confidence = BASE_CONFIDENCE
            if len(parsed["insights"]) >= MIN_INSIGHTS_FOR_HIGH_CONFIDENCE:
                confidence = HIGH_CONFIDENCE_THRESHOLD
            if (
                len(parsed["risks"]) >= MIN_RISKS_FOR_HIGH_CONFIDENCE
                and len(parsed["opportunities"]) >= MIN_OPPORTUNITIES_FOR_HIGH_CONFIDENCE
            ):
                confidence = VERY_HIGH_CONFIDENCE_THRESHOLD

            # Create summary
            summary = f"FinGPT {analysis_type.replace('_', ' ')} for {symbol}. "
            summary += f"Generated {len(parsed['insights'])} insights, "
            summary += f"{len(parsed['risks'])} risks, and "
            summary += f"{len(parsed['opportunities'])} opportunities."

            report = FinGPTGenerativeReport(
                agent_role=AgentRole.FINGPT_GENERATIVE_ANALYST,
                symbol=symbol,
                summary=summary,
                confidence=confidence,
                analysis_type=analysis_type,
                key_insights=parsed["insights"],
                risks_identified=parsed["risks"],
                opportunities_identified=parsed["opportunities"],
                detailed_summary=response[:1000],  # Store first 1000 chars
            )

            logger.info(
                "FinGPT generative analysis complete",
                symbol=symbol,
                insights_count=len(parsed["insights"]),
                confidence=confidence,
            )

            return report

        except Exception as e:
            logger.error(
                "FinGPT generative analysis failed", symbol=symbol, error=str(e)
            )

            return FinGPTGenerativeReport(
                agent_role=AgentRole.FINGPT_GENERATIVE_ANALYST,
                symbol=symbol,
                summary=f"Analysis failed: {str(e)}",
                confidence=0.0,
                analysis_type=analysis_type,
                key_insights=["Analysis error occurred"],
                risks_identified=[],
                opportunities_identified=[],
                detailed_summary="",
            )
