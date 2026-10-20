import pytest

from models import Position, Robot, Task, Warehouse
from optimizer import NoPathError, a_star_path, optimize_path


def test_a_star_routes_around_obstacle():
    warehouse = Warehouse(
        width=3,
        height=3,
        obstacles=[Position(x=1, y=0)],
    )

    path = a_star_path(
        Position(x=0, y=0),
        Position(x=2, y=0),
        warehouse,
    )

    assert path[0] == Position(x=0, y=0)
    assert path[-1] == Position(x=2, y=0)
    assert len(path) == 5
    assert Position(x=1, y=0) not in path
    assert all(
        abs(a.x - b.x) + abs(a.y - b.y) == 1
        for a, b in zip(path, path[1:])
    )


def test_a_star_raises_when_goal_is_unreachable():
    warehouse = Warehouse(
        width=3,
        height=3,
        obstacles=[
            Position(x=1, y=0),
            Position(x=1, y=1),
            Position(x=1, y=2),
        ],
    )

    with pytest.raises(NoPathError):
        a_star_path(
            Position(x=0, y=1),
            Position(x=2, y=1),
            warehouse,
        )


def test_optimize_path_raises_when_assigned_task_is_unreachable():
    warehouse = Warehouse(
        width=5,
        height=3,
        obstacles=[
            Position(x=1, y=0),
            Position(x=1, y=1),
            Position(x=1, y=2),
        ],
    )
    agent = Robot(id="robot-1", position=Position(x=0, y=1))
    near_but_unreachable = Task(
        id="task-b",
        name="Across wall",
        position=Position(x=2, y=1),
        priority=5,
    )
    reachable = Task(
        id="task-a",
        name="Same side",
        position=Position(x=0, y=2),
        priority=1,
    )

    with pytest.raises(ValueError, match="No remaining task is reachable"):
        optimize_path(agent, [near_but_unreachable, reachable], warehouse)


def test_optimize_path_orders_reachable_tasks_by_a_star_distance():
    warehouse = Warehouse(width=5, height=5)
    agent = Robot(id="robot-1", position=Position(x=0, y=0))
    farther = Task(
        id="task-b",
        name="Far task",
        position=Position(x=4, y=4),
        priority=5,
    )
    nearer = Task(
        id="task-a",
        name="Near task",
        position=Position(x=1, y=0),
        priority=1,
    )

    assert optimize_path(agent, [farther, nearer], warehouse) == [nearer, farther]
