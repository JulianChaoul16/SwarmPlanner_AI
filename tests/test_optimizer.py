import pytest

from models import Mission, Position, Robot, Task, Warehouse
from optimizer import allocate_tasks, distance


def make_mission(robots, tasks):
    return Mission(
        id="mission-1",
        objective="Inspect warehouse",
        warehouse=Warehouse(width=20, height=20),
        robots=robots,
        tasks=tasks,
    )


def task(task_id, x, y=0, priority=1, duration=2.0):
    return Task(
        id=task_id, name=f"Inspect {task_id}",
        position=Position(x=x, y=y), priority=priority, duration=duration,
    )


def test_distance_uses_euclidean_distance():
    assert distance(Position(x=0, y=0), Position(x=3, y=4)) == pytest.approx(5)


def test_schedules_by_priority_then_task_id():
    mission = make_mission(
        [Robot(id="R1", position=Position(x=0, y=0))],
        [task("C", 1), task("B", 8, priority=5), task("A", 4, priority=5)],
    )
    plan = allocate_tasks(mission)
    assert [a.task_id for a in plan.assignments] == ["A", "B", "C"]


def test_tracks_robot_endpoint_workload_and_plan_totals():
    mission = make_mission(
        [Robot(id="R1", position=Position(x=0, y=0), speed=2)],
        [task("A", 3, 4, duration=2), task("B", 6, 8, duration=3)],
    )
    plan = allocate_tasks(mission)
    assert [a.robot_id for a in plan.assignments] == ["R1", "R1"]
    assert [a.start_time for a in plan.assignments] == pytest.approx([0, 4.5])
    assert [a.finish_time for a in plan.assignments] == pytest.approx([4.5, 10])
    assert plan.makespan == pytest.approx(10)
    assert plan.total_distance == pytest.approx(10)


def test_selects_earliest_finishing_robot_including_speed_and_workload():
    mission = make_mission(
        [
            Robot(id="near", position=Position(x=4, y=0)),
            Robot(id="fast", position=Position(x=0, y=0), speed=10),
        ],
        [task("A", 5, priority=5, duration=10), task("B", 5)],
    )
    plan = allocate_tasks(mission)
    assert [a.robot_id for a in plan.assignments] == ["fast", "near"]
    assert [a.start_time for a in plan.assignments] == pytest.approx([0, 0])
    assert [a.finish_time for a in plan.assignments] == pytest.approx([10.5, 3])
    assert plan.makespan == pytest.approx(10.5)
    assert plan.total_distance == pytest.approx(6)


def test_equal_finish_times_favor_lower_workload():
    mission = make_mission(
        [
            Robot(id="A", position=Position(x=0, y=0)),
            Robot(id="B", position=Position(x=4, y=0)),
        ],
        [task("first", 0, priority=5, duration=4), task("second", 0)],
    )
    plan = allocate_tasks(mission)
    assert [a.robot_id for a in plan.assignments] == ["A", "B"]
    assert plan.assignments[1].finish_time == pytest.approx(6)


def test_equal_finish_times_and_workloads_favor_robot_id():
    mission = make_mission(
        [
            Robot(id="B", position=Position(x=0, y=0)),
            Robot(id="A", position=Position(x=0, y=0)),
        ],
        [task("only", 1)],
    )
    plan = allocate_tasks(mission)
    assert len(plan.assignments) == 1
    assert plan.assignments[0].robot_id == "A"
