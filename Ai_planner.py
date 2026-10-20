import json
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


def get_mission() -> str:
    return input("Enter the mission details: ").strip()


def get_plan(mission: str) -> dict[str, Any]:
    """Turn mission details into a structured task plan."""
    if not mission.strip():
        raise ValueError("Mission details cannot be empty.")

    response = OpenAI().responses.create(
        model="gpt-4.1-mini",
        instructions=(
            "You are SwarmPlanner, an AI mission planner for autonomous robot "
            "fleets in a warehouse. Break the mission into tasks, considering "
            "priorities, skills, and constraints. Do not invent robot "
            "capabilities or locations. Return a JSON object with a 'tasks' "
            "array. Each task must have these fields: id (string), name "
            "(string), position ([x, y] coordinates or null if unspecified), "
            "priority (integer), and status (use 'pending')."
        ),
        input=mission,
        text={"format": {"type": "json_object"}},
    )

    return json.loads(response.output_text)


if __name__ == "__main__":
    print(json.dumps(get_plan(get_mission()), indent=2))
