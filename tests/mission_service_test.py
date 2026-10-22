
import pytest
from pydantic import ValidationError

from models import Warehouse, Robot, Position
from Ai_parser import ParsedMission, ParsedTask
from mission_service import MissionService


class FakeParser:
    def parse(self, prompt, width, height):
        return ParsedMission(
            objective="Inspect warehouse",
            tasks=[
                ParsedTask(
                    name="Inspect loading dock",
                    x=3,
                    y=4,
                    priority=5,
                    duration=2.0
                ),
                ParsedTask(
                    name="Inspect storage",
                    x=7,
                    y=2,
                    priority=3,
                    duration=3.0
                )
            ]
        )


def test_ai_mission_integration():
    service = MissionService(FakeParser())

    warehouse = Warehouse(width=10, height=10)

    robots = [
        Robot(
            id="R1",
            position=Position(x=0, y=0)
        ),
        Robot(
            id="R2",
            position=Position(x=9, y=9)
        )
    ]

    mission, plan = service.create_plan(
        "Inspect the loading dock and storage",
        warehouse,
        robots
    )

    assert len(mission.tasks) == 2
    assert len(plan.assignments) == 2
    assert {a.task_id for a in plan.assignments} == {
        "T1", "T2"
    }
    assert plan.makespan > 0


def test_rejects_invalid_ai_coordinates():
    class InvalidParser:
        def parse(self, prompt, width, height):
            return ParsedMission(
                objective="Invalid mission",
                tasks=[
                    ParsedTask(
                        name="Outside warehouse",
                        x=100,
                        y=100,
                        priority=5,
                        duration=2.0
                    )
                ]
            )

    service = MissionService(InvalidParser())

    with pytest.raises(ValidationError):
        service.create_plan(
            "Inspect the warehouse",
            Warehouse(width=10, height=10),
            [
                Robot(
                    id="R1",
                    position=Position(x=0, y=0)
                )
            ]
        )


def test_rejects_obstacle_task():
    class BlockedParser:
        def parse(self, prompt, width, height):
            return ParsedMission(
                objective="Blocked mission",
                tasks=[
                    ParsedTask(
                        name="Blocked inspection",
                        x=5,
                        y=5,
                        priority=5,
                        duration=2.0
                    )
                ]
            )

    service = MissionService(BlockedParser())

    with pytest.raises(ValidationError):
        service.create_plan(
            "Inspect blocked location",
            Warehouse(
                width=10,
                height=10,
                obstacles=[Position(x=5, y=5)]
            ),
            [
                Robot(
                    id="R1",
                    position=Position(x=0, y=0)
                )
            ]
        )
