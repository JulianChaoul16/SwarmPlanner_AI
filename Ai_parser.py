
import os

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field

load_dotenv()


class ParsedTask(BaseModel):
    name: str
    x: int
    y: int
    priority: int
    duration: float


class ParsedMission(BaseModel):
    objective: str
    tasks: list[ParsedTask]


class OpenAIMissionParser:
    def __init__(self, client=None):
        self.client = client or OpenAI(
            api_key=os.environ["OPENAI_API_KEY"]
        )

    def parse(self, prompt: str, width: int, height: int):
        if not prompt.strip():
            raise ValueError("Mission description is empty")

        response = self.client.responses.parse(
            model="gpt-4.1-mini",
            instructions=(
                "You interpret warehouse inspection requests. "
                "Return 1 to 8 actionable inspection tasks. "
                "Priority ranges from 1 (low) to 5 (high). "
                "Duration is in simulated minutes and must "
                "be nonnegative. "
                f"The simulated grid has width {width} "
                f"and height {height}. "
                "Choose illustrative coordinates inside "
                "that grid when real positions are unknown. "
                "Do not claim these are real warehouse "
                "coordinates. Do not assign robots."
            ),
            input=prompt,
            text_format=ParsedMission,
        )

        if response.output_parsed is None:
            raise ValueError("No structured mission returned")

        return response.output_parsed
