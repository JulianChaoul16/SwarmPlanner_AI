
import pytest
from pydantic import ValidationError

from models import (
    Position,
    Robot,
    Task,
    Warehouse,
    Mission,
)


def make_mission():
    return Mission(
        id="mission-001",
        objective="Inspect the warehouse",
        warehouse=Warehouse(
            width=10,
            height=10,
            obstacles=[Position(x=5, y=5)]
        ),
        robots=[
            Robot(
                id="robot-1",
                position=Position(x=0, y=0)
            )
        ],
        tasks=[
            Task(
                id="task-1",
                name="Inspect loading dock",
                position=Position(x=8, y=8),
                priority=5
            )
        ]
    )


def test_valid_mission():
    mission = make_mission()
    assert len(mission.robots) == 1
    assert len(mission.tasks) == 1


def test_invalid_priority():
    with pytest.raises(ValidationError):
        Task(
            id="task-2",
            name="Invalid task",
            position=Position(x=2, y=2),
            priority=10
        )


def test_robot_outside_warehouse():
    mission = make_mission()
    data = mission.model_dump()
    data["robots"][0]["position"] = {"x": 20, "y": 0}

    with pytest.raises(ValidationError):
        Mission.model_validate(data)


def test_task_on_obstacle():
    mission = make_mission()
    data = mission.model_dump()
    data["tasks"][0]["position"] = {"x": 5, "y": 5}

    with pytest.raises(ValidationError):
        Mission.model_validate(data)


def test_duplicate_robot_ids():
    mission = make_mission()
    data = mission.model_dump()
    data["robots"].append(data["robots"][0].copy())

    with pytest.raises(ValidationError):
        Mission.model_validate(data)
