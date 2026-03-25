"""
TECHIN 510 Week 7 - Tool Definitions and Execution
====================================================
This is where you define the "tools" your chatbot can use.

Think of tools like apps on your phone -- the LLM is the user who
decides which app to open based on what it needs to do. You define
what each app does, what inputs it needs, and what it returns.

The Anthropic API uses a specific format for tool definitions.
Each tool needs:
  - name: a unique identifier (like a function name)
  - description: tells the LLM WHEN to use this tool
  - input_schema: tells the LLM WHAT inputs the tool needs (JSON Schema)
"""

# ============================================================================
# TOOL DEFINITIONS
# ============================================================================
# These are the "menus" you hand to the LLM -- it reads these to decide
# which tool to call. The descriptions are critically important because
# that is how the LLM decides which tool matches the user's question.
# ============================================================================

EQUIPMENT_STATUS_TOOL = {
    "name": "check_equipment_status",
    "description": (
        "Check whether a specific makerspace equipment is available, in use, "
        "or under maintenance. Use this tool when the user asks if a piece of "
        "equipment is available -- e.g., 3D printer, laser cutter, soldering station."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "equipment_name": {
                "type": "string",
                "description": (
                    "Name of the equipment to check (e.g., '3D printer', "
                    "'laser cutter', 'soldering station')."
                ),
            }
        },
        "required": ["equipment_name"],
    },
}


LAB_POLICY_TOOL = {
    "name": "lookup_lab_policy",
    "description": (
        "Look up GIX makerspace policies by topic. Use this tool when the user "
        "asks about safety training, makerspace hours, checkout/booking process, "
        "or policies for 3D printing, laser cutting, or soldering."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "topic": {
                "type": "string",
                "description": (
                    "Policy topic to look up (e.g., 'safety training', 'hours', "
                    "'checkout', '3D printing', 'laser cutting', 'soldering')."
                ),
            }
        },
        "required": ["topic"],
    },
}


# ============================================================================
# TODO (Level 4): Add your custom third tool here.
# ============================================================================
# Examples: check_training_status, search_equipment_manual, check_makerspace_schedule,
# lookup_contact. Define the tool dict and its execute_ function below, then
# add it to get_all_tools() and execute_tool().
# ============================================================================


# ============================================================================
# BAD TOOL DEFINITION — Counter-example for Tool Design Principles exercise
# ============================================================================
# This tool violates several design principles. Can you spot the problems?
# (Used in Level 4 to discuss what makes a good vs bad tool definition.)

BAD_TOOL_EXAMPLE = {
    "name": "do_stuff",
    "description": "Does things for the makerspace.",
    "input_schema": {
        "type": "object",
        "properties": {
            "data": {
                "type": "string",
                "description": "The data.",
            }
        },
        "required": ["data"],
    },
}
# Problems:
# 1. Name is vague ("do_stuff") — violates single responsibility
# 2. Description is useless ("Does things") — LLM cannot decide when to call it
# 3. Input parameter is generic ("data") — no explicit contract
# 4. No indication of what it returns — unpredictable output format
# 5. Tries to do everything — should be split into specific tools


# ============================================================================
# TOOL EXECUTION
# ============================================================================
# These functions actually DO the work when the LLM decides to call a tool.
# The LLM sends back "I want to call check_equipment_status with equipment_name='laser cutter'"
# and these functions run and return the result.
# ============================================================================

def execute_check_equipment_status(equipment_name: str) -> str:
    """
    Return simulated status for a makerspace equipment.

    In a real application, you would integrate with an equipment inventory
    or booking system. For this lab, we use simulated data so you can
    focus on the agentic pattern.
    """
    # Simulated status for key fabrication equipment
    equipment_status = {
        "3d printer": {"status": "available", "note": "Next reservation in 2 hours."},
        "3d printers": {"status": "available", "note": "Two units available."},
        "laser cutter": {"status": "in use", "note": "Expected free by 3:00 PM."},
        "laser cutters": {"status": "in use", "note": "One in use, one available."},
        "soldering station": {"status": "available", "note": "All stations free."},
        "soldering": {"status": "available", "note": "Soldering stations are available."},
    }

    key = equipment_name.strip().lower()
    if key in equipment_status:
        info = equipment_status[key]
        return (
            f"{equipment_name}: {info['status'].upper()}. {info['note']} "
            "(Simulated data for lab purposes.)"
        )
    # Fuzzy match for common variants
    for known, info in equipment_status.items():
        if known in key or key in known:
            return (
                f"{equipment_name}: {info['status'].upper()}. {info['note']} "
                "(Simulated data for lab purposes.)"
            )
    return (
        f"I don't have status information for '{equipment_name}'. "
        "That equipment may be managed separately. Please check with makerspace staff "
        "or the equipment board in the makerspace."
    )


def execute_lookup_lab_policy(topic: str) -> str:
    """
    Return simulated makerspace policy for a topic.

    In a real application, you would query a policy database or wiki.
    For this lab, we use simulated data.
    """
    policies = {
        "safety training": (
            "All users must complete the general makerspace safety orientation before "
            "using any equipment. Additional equipment-specific training is required "
            "for the laser cutter and 3D printers. Soldering requires a short "
            "soldering safety module. Sign up via the makerspace portal."
        ),
        "hours": (
            "Makerspace hours: Mon–Fri 9am–9pm, Sat 10am–5pm. Closed Sundays and "
            "university holidays. (Spring 2026 schedule.)"
        ),
        "checkout": (
            "Equipment checkout is done in person at the makerspace desk. Bring your "
            "student ID and confirm you have completed required training. Staff will "
            "confirm availability and hand off the equipment. No self-service checkout."
        ),
        "booking": (
            "You can reserve the laser cutter and 3D printers via the makerspace "
            "booking system. Soldering stations are first-come, first-served. "
            "Reservations require completed training."
        ),
        "3d printing": (
            "3D printing: Complete general safety + 3D printer training. Maximum "
            "print time per session may apply. Use only approved materials. "
            "Check policy board for current material list."
        ),
        "laser cutting": (
            "Laser cutting: Complete general safety + laser cutter certification. "
            "Only approved materials (e.g., wood, acrylic, paper). No vinyl or PVC. "
            "Book a slot; walk-ins subject to availability."
        ),
        "soldering": (
            "Soldering: Complete general safety + soldering module. Stations are "
            "first-come, first-served. Ventilation must be on. Return tools when done."
        ),
    }

    key = topic.strip().lower()
    if key in policies:
        return f"Makerspace policy ({topic}): {policies[key]} (Simulated data.)"
    for known, text in policies.items():
        if known in key or key in known:
            return f"Makerspace policy ({topic}): {text} (Simulated data.)"
    return (
        f"I don't have a specific policy for '{topic}'. For other questions, "
        "contact the makerspace staff or check the policy board in the space."
    )


# ============================================================================
# TOOL REGISTRY
# ============================================================================
# This maps tool names to their execution functions, so the app can look up
# which function to call when the LLM returns a tool_use block.
# ============================================================================

def get_all_tools() -> list[dict]:
    """Return the list of all tool definitions to send to the Anthropic API."""
    return [EQUIPMENT_STATUS_TOOL, LAB_POLICY_TOOL]
    # TODO (Level 4): After adding your custom tool, include it:
    # return [EQUIPMENT_STATUS_TOOL, LAB_POLICY_TOOL, MY_CUSTOM_TOOL]


def execute_tool(tool_name: str, tool_input: dict) -> str:
    """
    Execute a tool by name and return the result as a string.
    This is the "dispatcher" -- it routes the LLM's tool call
    to the right Python function.
    """
    if tool_name == "check_equipment_status":
        return execute_check_equipment_status(tool_input["equipment_name"])
    elif tool_name == "lookup_lab_policy":
        return execute_lookup_lab_policy(tool_input["topic"])
    # TODO (Level 4): Add branch for your custom tool, e.g.:
    # elif tool_name == "check_training_status":
    #     return execute_check_training_status(tool_input["equipment_name"])
    else:
        return f"Error: Unknown tool '{tool_name}'"
