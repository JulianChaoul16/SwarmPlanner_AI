
from dataclasses import dataclass


@dataclass
class Agent:
    """Agent Robots within the warehouse"""

    id: str
    task: Task
    position: tuple




@dataclass

class Task:
    """Task to be completed by the agent robots"""

    id: str
    name: str
    position: tuple
    priority: int
    status: str = "pending"