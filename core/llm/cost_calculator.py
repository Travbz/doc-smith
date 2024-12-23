from typing import Dict, Optional
import logging
from dataclasses import dataclass
from ..utils.logging_config import setup_logger

logger = setup_logger(__name__)

@dataclass
class ModelPricing:
    input_price: float  # Price per 1K input tokens
    output_price: float  # Price per 1K output tokens

# Model pricing in USD per 1K tokens
MODEL_PRICING = {
    "gpt-4-turbo-preview": ModelPricing(
        input_price=0.01,
        output_price=0.03
    ),
    "gpt-4": ModelPricing(
        input_price=0.03,
        output_price=0.06
    ),
    "gpt-3.5-turbo-1106": ModelPricing(
        input_price=0.001,
        output_price=0.002
    ),
    "gpt-3.5-turbo": ModelPricing(
        input_price=0.001,
        output_price=0.002
    )
}

class CostTracker:
    def __init__(self):
        self.total_cost: float = 0.0
        self.requests: int = 0
        self.total_tokens: int = 0
        self.model_usage: Dict[str, Dict[str, float]] = {}

    def add_request(self, model: str, input_tokens: int, output_tokens: int) -> None:
        """Track the cost of a request."""
        cost = calculate_cost(input_tokens, model, output_tokens)
        self.total_cost += cost
        self.requests += 1
        self.total_tokens += input_tokens + output_tokens

        if model not in self.model_usage:
            self.model_usage[model] = {
                "cost": 0.0,
                "requests": 0,
                "total_tokens": 0
            }

        self.model_usage[model]["cost"] += cost
        self.model_usage[model]["requests"] += 1
        self.model_usage[model]["total_tokens"] += input_tokens + output_tokens

    def get_summary(self) -> Dict[str, any]:
        """Get a summary of usage and costs."""
        return {
            "total_cost": self.total_cost,
            "total_requests": self.requests,
            "total_tokens": self.total_tokens,
            "model_usage": self.model_usage,
            "average_cost_per_request": self.total_cost / self.requests if self.requests > 0 else 0
        }

def calculate_cost(
    input_tokens: int,
    model: str,
    output_tokens: Optional[int] = None
) -> float:
    """Calculate the cost for a given number of tokens."""
    if model not in MODEL_PRICING:
        logger.warning(f"Unknown model {model}, using gpt-3.5-turbo pricing")
        model = "gpt-3.5-turbo"

    pricing = MODEL_PRICING[model]
    input_cost = (input_tokens / 1000) * pricing.input_price
    
    if output_tokens is not None:
        output_cost = (output_tokens / 1000) * pricing.output_price
        return input_cost + output_cost
        
    return input_cost

def estimate_max_tokens_for_budget(
    budget: float,
    model: str,
    output_ratio: float = 0.5
) -> Dict[str, int]:
    """Estimate maximum tokens possible within a budget."""
    if model not in MODEL_PRICING:
        raise ValueError(f"Unknown model: {model}")

    pricing = MODEL_PRICING[model]
    
    # Assume output_ratio of the tokens will be output tokens
    # Example: if output_ratio is 0.5, half of tokens will be output tokens
    total_tokens = budget * 1000 / (
        pricing.input_price * (1 - output_ratio) +
        pricing.output_price * output_ratio
    )
    
    return {
        "total_tokens": int(total_tokens),
        "input_tokens": int(total_tokens * (1 - output_ratio)),
        "output_tokens": int(total_tokens * output_ratio)
    }

# Create a singleton instance
cost_tracker = CostTracker()