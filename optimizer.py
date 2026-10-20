from heapq import heappop, heappush
from itertools import count

from numpy import hypot

from models import Mission, Position, Robot, Task, Warehouse


class NoPathError(ValueError):
    """Raised when two valid warehouse positions are disconnected."""


def distance(a: Position, b: Position) -> float:
    return hypot(a.x - b.x, a.y - b.y)



def allocate_tasks(mission: Mission) -> dict[str, list[str]]:
    assignments = {
        robot.id: [] for robot in mission.robots
    }

    # Track each robot's planned endpoint.
    positions = {
        robot.id: robot.position
        for robot in mission.robots
    }

    tasks = sorted(
        mission.tasks,
        key=lambda task: (-task.priority, task.id)
    )

    for task in tasks:
        robot = min(
            mission.robots,
            key=lambda r: (
                distance(positions[r.id], task.position),
                len(assignments[r.id]),
                r.id
            )
        )

        assignments[robot.id].append(task.id)
        positions[robot.id] = task.position

    return assignments



def _manhattan_distance(start: tuple[int, int], goal: tuple[int, int]) -> int:
    return abs(start[0] - goal[0]) + abs(start[1] - goal[1])


def a_star_path(
    start: Position,
    goal: Position,
    warehouse: Warehouse,
) -> list[Position]:
    """Find a shortest four-directional grid path, including start and goal."""
    start_point = (start.x, start.y)
    goal_point = (goal.x, goal.y)

    for point in (start, goal):
        if not warehouse.contains(point):
            raise ValueError(
                f"Position ({point.x}, {point.y}) is outside the warehouse"
            )
        if warehouse.is_blocked(point):
            raise ValueError(
                f"Position ({point.x}, {point.y}) is blocked by an obstacle"
            )

    frontier: list[tuple[int, int, tuple[int, int]]] = []
    sequence = count()
    heappush(
        frontier,
        (_manhattan_distance(start_point, goal_point), next(sequence), start_point),
    )
    came_from: dict[tuple[int, int], tuple[int, int] | None] = {
        start_point: None
    }
    cost_so_far = {start_point: 0}
    directions = ((0, 1), (1, 0), (0, -1), (-1, 0))

    while frontier:
        _, _, current = heappop(frontier)
        if current == goal_point:
            path = []
            point: tuple[int, int] | None = current
            while point is not None:
                path.append(Position(x=point[0], y=point[1]))
                point = came_from[point]
            return list(reversed(path))

        for dx, dy in directions:
            neighbor = (current[0] + dx, current[1] + dy)
            if not (
                0 <= neighbor[0] < warehouse.width
                and 0 <= neighbor[1] < warehouse.height
            ):
                continue
            position = Position(x=neighbor[0], y=neighbor[1])
            if warehouse.is_blocked(position):
                continue

            new_cost = cost_so_far[current] + 1
            if neighbor in cost_so_far and new_cost >= cost_so_far[neighbor]:
                continue

            cost_so_far[neighbor] = new_cost
            came_from[neighbor] = current
            priority = new_cost + _manhattan_distance(neighbor, goal_point)
            heappush(frontier, (priority, next(sequence), neighbor))

    raise NoPathError(
        f"No path from ({start.x}, {start.y}) to ({goal.x}, {goal.y})"
    )


def optimize_path(
    agent: Robot,
    tasks: list[Task],
    warehouse: Warehouse,
) -> list[Task]:
    """Order tasks by repeatedly choosing the nearest reachable task via A*."""
    remaining = list(tasks)
    ordered: list[Task] = []
    current = agent.position

    while remaining:
        candidates = []
        for task in remaining:
            try:
                path = a_star_path(current, task.position, warehouse)
            except NoPathError:
                continue
            candidates.append((len(path) - 1, task.id, task, path))

        if not candidates:
            raise ValueError(
                f"No remaining task is reachable from robot {agent.id}"
            )

        _, _, task, path = min(candidates, key=lambda candidate: (
            candidate[0], candidate[1]
        ))
        ordered.append(task)
        remaining.remove(task)
        current = path[-1]

    return ordered


def schedule_tasks(mission: Mission) -> dict[str, list[Task]]:
    """Allocate mission tasks to robots and order each robot's route."""
    tasks_by_id = {task.id: task for task in mission.tasks}
    assignments = allocate_tasks(mission)

    return {
        robot.id: optimize_path(
            robot,
            [tasks_by_id[task_id] for task_id in assignments[robot.id]],
            mission.warehouse,
        )
        for robot in mission.robots
    }
