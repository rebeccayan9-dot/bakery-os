"""
TECHIN 510 Week 7 - GIX Makerspace Assistant (Agentic AI Starter Kit)
======================================================================
A Streamlit chatbot that uses the Anthropic API with tool use (function calling).
Helps with the GIX makerspace: fabrication (3D printing, soldering, laser cutting),
equipment availability, and makerspace policies.

This app demonstrates:
  - Calling an LLM from your application
  - Tool use / function calling (the core of "agentic AI")
  - System prompts as product specification
  - Cost tracking and production awareness
  - Guardrails and edge case handling

Run with:  streamlit run app.py
"""

import json
import streamlit as st
from utils import (
    get_anthropic_client,
    debug_log,
    format_tool_result_for_display,
    validate_user_input,
    retry_api_call,
    calculate_cost,
    format_cost_display,
    project_cost_at_scale,
    check_prompt_injection,
)
from tools import get_all_tools, execute_tool
from prompts import MAKERSPACE_ASSISTANT_V1

# ---------------------------------------------------------------------------
# Active system prompt — change this import to switch versions (Level 4)
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = MAKERSPACE_ASSISTANT_V1


def _serialize_content_blocks(content) -> list[dict]:
    """Convert Anthropic SDK content blocks (Pydantic objects) to plain dicts.

    The Anthropic SDK returns TextBlock / ToolUseBlock model objects, not
    dicts.  If we store them directly in session state, isinstance(block, dict)
    checks fail on Streamlit page reruns.  Converting once at storage time
    avoids that problem.
    """
    serialized = []
    for block in content:
        if hasattr(block, "model_dump"):
            serialized.append(block.model_dump())
        elif isinstance(block, dict):
            serialized.append(block)
        else:
            serialized.append({"type": "text", "text": str(block)})
    return serialized

# ---------------------------------------------------------------------------
# Page configuration -- this must be the very first Streamlit command
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Week 7: GIX Makerspace Assistant",
    page_icon="\U0001f916",
    layout="wide",
)


# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================
# Streamlit re-runs the entire script on every interaction. Session state is
# how we remember things between reruns -- like the conversation history.
# Think of it as the app's "short-term memory."
# ============================================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "tool_call_history" not in st.session_state:
    st.session_state.tool_call_history = []

if "total_cost" not in st.session_state:
    st.session_state.total_cost = 0.0

if "total_input_tokens" not in st.session_state:
    st.session_state.total_input_tokens = 0

if "total_output_tokens" not in st.session_state:
    st.session_state.total_output_tokens = 0


# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    st.header("Settings")

    # Model selection
    model = st.selectbox(
        "Model",
        ["claude-sonnet-4-20250514", "claude-haiku-4-20250414"],
        index=0,
        help="Sonnet is more capable; Haiku is faster and cheaper.",
    )

    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.0,
        value=0.3,
        step=0.1,
        help="Lower = more focused/deterministic. Higher = more creative/varied.",
    )

    max_tokens = st.slider(
        "Max tokens",
        min_value=256,
        max_value=4096,
        value=1024,
        step=256,
        help="Maximum length of the response. 1 token is roughly 4 characters.",
    )

    st.divider()

    # Show which tools are active
    st.subheader("Active Tools")
    tools = get_all_tools()
    for tool in tools:
        st.markdown(f"- **{tool['name']}**: {tool['description'][:80]}...")

    st.divider()

    # -----------------------------------------------------------------------
    # Cost tracking panel
    # -----------------------------------------------------------------------
    st.subheader("Cost Tracker")
    if st.session_state.total_cost > 0:
        st.markdown(
            f"**Session total:** ${st.session_state.total_cost:.4f}\n\n"
            f"**Tokens used:** {st.session_state.total_input_tokens:,} in / "
            f"{st.session_state.total_output_tokens:,} out"
        )
        # Project cost at scale — the Level 1 exercise question
        if st.session_state.tool_call_history:
            num_queries = len([
                m for m in st.session_state.messages if isinstance(m, dict) and m.get("role") == "user" and isinstance(m.get("content"), str)
            ])
            if num_queries > 0:
                avg_cost = st.session_state.total_cost / num_queries
                st.markdown(project_cost_at_scale(avg_cost, 100, 5))
    else:
        st.markdown("*No API calls yet.*")

    st.divider()

    # Tool call history for debugging
    if st.session_state.tool_call_history:
        st.subheader("Tool Call History")
        for i, call in enumerate(st.session_state.tool_call_history):
            with st.expander(f"Call {i + 1}: {call['tool_name']}"):
                st.json(call)

    st.divider()

    # Clear conversation button
    if st.button("Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.tool_call_history = []
        st.session_state.total_cost = 0.0
        st.session_state.total_input_tokens = 0
        st.session_state.total_output_tokens = 0
        st.rerun()


# ============================================================================
# MAIN CHAT INTERFACE
# ============================================================================

st.title("Team Pilot Bot")
st.caption(
    "Your team coordination assistant — find meeting times, split costs, and track tasks. "
    "Try: 'When can our team meet on Wednesday?' or 'Split $127.50 across 4 people.'"
)

# Display existing conversation history
for message in st.session_state.messages:
    role = message["role"]
    if role == "user":
        with st.chat_message("user"):
            if isinstance(message["content"], str):
                st.markdown(message["content"])
            elif isinstance(message["content"], list):
                for block in message["content"]:
                    if isinstance(block, dict) and block.get("type") == "text":
                        st.markdown(block["text"])
    elif role == "assistant":
        with st.chat_message("assistant"):
            if isinstance(message["content"], str):
                st.markdown(message["content"])
            elif isinstance(message["content"], list):
                for block in message["content"]:
                    if isinstance(block, dict):
                        if block.get("type") == "text":
                            st.markdown(block["text"])
                        elif block.get("type") == "tool_use":
                            with st.expander(f"Used tool: {block['name']}"):
                                st.json(block["input"])


# ============================================================================
# AGENTIC LOOP: THE CORE OF TOOL USE
# ============================================================================
# This is where the magic happens. The "agentic loop" works like this:
#
#   1. User sends a message
#   2. We send it to the LLM along with the tool definitions
#   3. The LLM either:
#      a. Responds with text (no tool needed) --> we display it, done
#      b. Responds with a tool_use block --> we execute the tool,
#         send the result back to the LLM, and go back to step 3
#
# This loop continues until the LLM responds with text (stop_reason="end_turn").
# ============================================================================

def run_agentic_loop(
    client,
    model: str,
    system_prompt: str,
    messages: list,
    tools: list,
    temperature: float,
    max_tokens: int,
) -> str:
    """
    Run the agentic tool-use loop until the LLM produces a final text response.

    Returns the final text response from the LLM.
    """
    final_text = ""
    current_messages = list(messages)  # Copy so we don't mutate the original

    # Safety limit to prevent infinite loops
    max_iterations = 10

    for iteration in range(max_iterations):
        debug_log(f"Iteration {iteration + 1}", {"num_messages": len(current_messages)})

        # -----------------------------------------------------------------
        # Call the Anthropic API (with retry for transient errors)
        # -----------------------------------------------------------------
        try:
            response = retry_api_call(
                lambda: client.messages.create(
                    model=model,
                    max_tokens=max_tokens,
                    system=system_prompt,
                    tools=tools,
                    messages=current_messages,
                    temperature=temperature,
                )
            )
        except Exception as e:
            error_msg = str(e)
            if "authentication" in error_msg.lower() or "api key" in error_msg.lower():
                return "API authentication error. Please check your ANTHROPIC_API_KEY in the .env file."
            elif "rate" in error_msg.lower():
                return "Rate limit reached. Please wait a moment and try again."
            else:
                return f"API error: {error_msg}"

        # -----------------------------------------------------------------
        # Track cost
        # -----------------------------------------------------------------
        cost_data = calculate_cost(
            model=model,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
        )
        st.session_state.total_cost += cost_data["total_cost"]
        st.session_state.total_input_tokens += cost_data["input_tokens"]
        st.session_state.total_output_tokens += cost_data["output_tokens"]

        debug_log("API Response", {
            "stop_reason": response.stop_reason,
            "content_blocks": len(response.content),
            "cost": f"${cost_data['total_cost']:.4f}",
        })

        # -----------------------------------------------------------------
        # Process the response content blocks
        # -----------------------------------------------------------------
        tool_use_blocks = []
        text_parts = []

        for block in response.content:
            if block.type == "text":
                text_parts.append(block.text)
            elif block.type == "tool_use":
                tool_use_blocks.append(block)

        # If the LLM stopped because it is done (no more tool calls), return
        if response.stop_reason == "end_turn":
            final_text = "\n".join(text_parts)
            current_messages.append({
                "role": "assistant",
                "content": _serialize_content_blocks(response.content),
            })
            break

        # -----------------------------------------------------------------
        # If the LLM wants to use tools, execute them
        # -----------------------------------------------------------------
        if response.stop_reason == "tool_use" and tool_use_blocks:
            current_messages.append({
                "role": "assistant",
                "content": _serialize_content_blocks(response.content),
            })

            # Execute each tool and collect results
            tool_results = []
            for tool_block in tool_use_blocks:
                tool_name = tool_block.name
                tool_input = tool_block.input

                # Show step-by-step progress with st.status
                with st.status(f"Calling tool: {tool_name}...", expanded=False) as status:
                    st.write(f"**Input:** `{json.dumps(tool_input)}`")

                    # Execute the tool with error handling
                    try:
                        result = execute_tool(tool_name, tool_input)
                    except Exception as e:
                        result = (
                            f"Error executing tool '{tool_name}': {str(e)}. "
                            f"The tool encountered a problem. Please try rephrasing your request."
                        )

                    st.write(f"**Result:** {result[:200]}{'...' if len(result) > 200 else ''}")
                    status.update(label=f"Used tool: {tool_name}", state="complete")

                debug_log(f"Tool: {tool_name}", {
                    "input": tool_input,
                    "result": result,
                })

                # Log tool call for the sidebar history
                st.session_state.tool_call_history.append({
                    "tool_name": tool_name,
                    "input": tool_input,
                    "result": result,
                })

                # Display tool usage in the chat
                with st.expander(f"Used tool: {tool_name}", expanded=False):
                    st.markdown(format_tool_result_for_display(
                        tool_name, tool_input, result
                    ))

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_block.id,
                    "content": result,
                })

            # Add tool results to the conversation
            current_messages.append({"role": "user", "content": tool_results})
        else:
            # Unexpected stop reason
            final_text = "\n".join(text_parts) if text_parts else "I could not generate a response."
            break

    # Update the session state messages with the full conversation
    st.session_state.messages = current_messages

    return final_text


# ============================================================================
# CHAT INPUT HANDLER
# ============================================================================

if user_input := st.chat_input("Ask Team Pilot... try scheduling, cost splitting, or task tracking!"):
    # Validate input
    is_valid, error_msg = validate_user_input(user_input)
    if not is_valid:
        st.error(error_msg)
        st.stop()

    # Check for prompt injection (educational — log but don't block)
    is_suspicious, matched_pattern = check_prompt_injection(user_input)
    if is_suspicious:
        debug_log("Prompt injection detected", {"pattern": matched_pattern, "input": user_input})

    # Display the user's message
    with st.chat_message("user"):
        st.markdown(user_input)

    # Add user message to conversation history
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Get the Anthropic client
    client = get_anthropic_client()

    # Run the agentic loop and display the response
    with st.chat_message("assistant"):
        response_text = run_agentic_loop(
            client=client,
            model=model,
            system_prompt=SYSTEM_PROMPT,
            messages=st.session_state.messages,
            tools=tools,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        # Display the final response
        st.markdown(response_text)
