
from uuid import uuid4

from models import Mission, Task, Position
from optimizer import allocate_tasks


class MissionService:
    def __init__(self, parser):
        self.parser = parser

    def create_plan(self, prompt, warehouse, robots):
        parsed = self.parser.parse(
            prompt,
            warehouse.width,
            warehouse.height
        )

        if not 1 <= len(parsed.tasks) <= 8:
            raise ValueError("Expected 1 to 8 tasks")

        tasks = []

        for i, item in enumerate(parsed.tasks):
            tasks.append(
                Task(
                    id=f"T{i + 1}",
                    name=item.name,
                    position=Position(
                        x=item.x,
                        y=item.y
                    ),
                    priority=item.priority,
                    duration=item.duration
                )
            )

        mission = Mission(
            id=str(uuid4()),
            objective=parsed.objective,
            warehouse=warehouse,
            robots=robots,
            tasks=tasks
        )

        plan = allocate_tasks(mission)

        return mission, plan
