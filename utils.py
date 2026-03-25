"""
TECHIN 510 Week 7 - Utility Functions
=====================================
Helper functions for the chatbot starter kit.
Don't worry about this file too much -- it's just plumbing
that keeps the main app.py clean and focused.
"""

import os
import re
import time
import json
import streamlit as st
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Environment setup
# ---------------------------------------------------------------------------

load_dotenv()

DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"


def get_anthropic_client():
    """
    Create and return an Anthropic client.
    Shows a friendly error if the API key is missing.
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")

    if not api_key or api_key == "sk-ant-your-key-here":
        st.error(
            "**Anthropic API key not configured.**\n\n"
            "1. Open the `.env` file in your project folder.\n"
            "2. Replace `sk-ant-your-key-here` with your actual API key.\n"
            "3. Get a key at [console.anthropic.com](https://console.anthropic.com/settings/keys).\n"
            "4. Save the file and refresh this page."
        )
        st.stop()

    import anthropic
    return anthropic.Anthropic(api_key=api_key)


def debug_log(label: str, data) -> None:
    """
    Print debug information when DEBUG_MODE is enabled.
    This is like having X-ray vision into what the LLM is doing.
    """
    if DEBUG_MODE:
        st.sidebar.markdown(f"**DEBUG: {label}**")
        if isinstance(data, (dict, list)):
            st.sidebar.json(data)
        else:
            st.sidebar.code(str(data))


def format_tool_result_for_display(tool_name: str, tool_input: dict, tool_result: str) -> str:
    """
    Format a tool call and its result for display in the Streamlit UI.
    Makes the agent's "thinking" visible to the user.
    """
    input_str = json.dumps(tool_input, indent=2)
    return (
        f"**Tool called:** `{tool_name}`\n\n"
        f"**Input:**\n```json\n{input_str}\n```\n\n"
        f"**Result:**\n{tool_result}"
    )


def validate_user_input(user_input: str) -> tuple[bool, str]:
    """
    Basic input validation for user messages.
    Returns (is_valid, error_message).

    Think of this like a bouncer at the door -- it checks the input
    before letting it through to the (expensive) LLM API call.
    """
    if not user_input or not user_input.strip():
        return False, "Please enter a message."

    if len(user_input) > 10000:
        return False, "Message is too long. Please keep it under 10,000 characters."

    return True, ""


def retry_api_call(func, max_retries: int = 3, base_delay: float = 1.0):
    """
    Retry an API call with exponential backoff.
    Like knocking on a door -- if nobody answers, wait a bit longer
    and try again, but don't stand there forever.
    """
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            delay = base_delay * (2 ** attempt)
            debug_log(f"Retry {attempt + 1}/{max_retries}", f"Waiting {delay}s: {e}")
            time.sleep(delay)


# ============================================================================
# COST TRACKING
# ============================================================================
# Token-based cost calculator. Prices are approximate and may change —
# check https://docs.anthropic.com/en/docs/about-claude/pricing for current rates.
# ============================================================================

# Pricing per 1M tokens (USD) as of early 2026
MODEL_PRICING = {
    "claude-sonnet-4-20250514": {"input": 3.00, "output": 15.00},
    "claude-haiku-4-20250414": {"input": 0.80, "output": 4.00},
}


def calculate_cost(
    model: str,
    input_tokens: int,
    output_tokens: int,
) -> dict:
    """
    Calculate the cost of an API call based on token usage.

    Returns a dict with:
      - input_cost: cost for input tokens (USD)
      - output_cost: cost for output tokens (USD)
      - total_cost: combined cost (USD)
      - input_tokens: number of input tokens
      - output_tokens: number of output tokens

    If the model is not in our pricing table, uses Sonnet pricing as default.
    """
    pricing = MODEL_PRICING.get(model, MODEL_PRICING["claude-sonnet-4-20250514"])

    input_cost = (input_tokens / 1_000_000) * pricing["input"]
    output_cost = (output_tokens / 1_000_000) * pricing["output"]

    return {
        "input_cost": input_cost,
        "output_cost": output_cost,
        "total_cost": input_cost + output_cost,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
    }


def format_cost_display(cost_data: dict) -> str:
    """Format cost data for human-readable display."""
    return (
        f"**Tokens:** {cost_data['input_tokens']:,} in / {cost_data['output_tokens']:,} out\n"
        f"**Cost:** ${cost_data['total_cost']:.4f} "
        f"(${cost_data['input_cost']:.4f} input + ${cost_data['output_cost']:.4f} output)"
    )


def project_cost_at_scale(cost_per_query: float, num_users: int, queries_per_day: int, days: int = 30) -> str:
    """
    Project what this would cost at scale.
    Helps students understand why cost-aware prompting matters.
    """
    total = cost_per_query * num_users * queries_per_day * days
    return (
        f"At {num_users} users x {queries_per_day} queries/day x {days} days: "
        f"**${total:,.2f}/month**"
    )


# ============================================================================
# PROMPT INJECTION CHECK (Educational)
# ============================================================================
# This is a basic pattern-matching check for common prompt injection attempts.
# It is NOT production-grade — real applications need more sophisticated
# defenses. But it demonstrates the concept and catches obvious attempts.
# ============================================================================

INJECTION_PATTERNS = [
    r"ignore (?:all |your |previous |the above )(?:instructions|rules|guidelines|prompts)",
    r"you are now",
    r"new instructions:",
    r"system prompt:",
    r"forget (?:all |your |everything|the above)",
    r"pretend you are",
    r"act as (?:a |an )?(?:different|new)",
    r"override (?:your |the )(?:instructions|rules|guidelines)",
    r"disregard (?:all |your |previous )",
]


def check_prompt_injection(user_input: str) -> tuple[bool, str]:
    """
    Check for common prompt injection patterns.
    Returns (is_suspicious, matched_pattern).

    This is educational — it shows the concept of input filtering.
    Production systems use more advanced techniques (classifier models,
    canary tokens, input/output sandboxing).
    """
    lowered = user_input.lower().strip()

    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, lowered):
            return True, pattern

    return False, ""
