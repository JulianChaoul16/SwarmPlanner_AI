
from math import hypot
from pydantic import BaseModel, Field

from models import Mission, Position


class Assignment(BaseModel):
    task_id: str
    robot_id: str
    start_time: float
    finish_time: float


class Plan(BaseModel):
    assignments: list[Assignment]
    makespan: float = Field(ge=0)
    total_distance: float = Field(ge=0)


def distance(a: Position, b: Position) -> float:
    return hypot(a.x - b.x, a.y - b.y)


def allocate_tasks(mission: Mission) -> Plan:
    # Track each robot's scheduled completion time.
    workload = {
        robot.id: 0.0
        for robot in mission.robots
    }

    # Track each robot's planned endpoint.
    positions = {
        robot.id: robot.position
        for robot in mission.robots
    }

    assignments = []
    total_distance = 0.0

    # Schedule higher-priority tasks first.
    tasks = sorted(
        mission.tasks,
        key=lambda t: (-t.priority, t.id)
    )

    for task in tasks:
        candidates = []

        for robot in mission.robots:
            travel_distance = distance(
                positions[robot.id],
                task.position
            )

            travel_time = travel_distance / robot.speed

            finish_time = (
                workload[robot.id]
                + travel_time
                + task.duration
            )

            candidates.append((
                finish_time,
                workload[robot.id],
                robot.id,
                travel_distance
            ))

        # Earliest completion, then lower workload,
        # then stable robot ID.
        best = min(candidates)
        finish_time, _, robot_id, travel_distance = best

        assignments.append(
            Assignment(
                task_id=task.id,
                robot_id=robot_id,
                start_time=workload[robot_id],
                finish_time=finish_time
            )
        )

        workload[robot_id] = finish_time
        positions[robot_id] = task.position
        total_distance += travel_distance

    return Plan(
        assignments=assignments,
        makespan=max(workload.values()),
        total_distance=total_distance
    )
