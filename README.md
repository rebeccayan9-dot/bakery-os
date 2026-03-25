# TECHIN 510 - Week 7: Agentic AI with Tool Use

## Overview
Build a GIX Staff Assistant chatbot with Anthropic API tool calling. Implement agentic loops, tool definitions, system prompts, guardrails, and adversarial testing.

## Setup
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Fill in your ANTHROPIC_API_KEY
streamlit run app.py
```

Or use the one-command setup:
```bash
chmod +x setup.sh && ./setup.sh
```

## Starter Code
- `app.py` — Main Streamlit app with agentic loop
- `tools.py` — Tool definitions (with TODO markers for custom tool)
- `prompts.py` — Versioned system prompts
- `utils.py` — API client, cost tracking, helpers
- `eval.py` — Evaluation checklist and test cases

## Instructions
See `lab-manual.md` for full lab instructions.
