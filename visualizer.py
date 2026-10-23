"""Streamlit warehouse visualization shared by the application."""

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import streamlit as st

from models import Robot, Task, Warehouse
from optimizer import Plan


def visualize_warehouse(
    warehouse: Warehouse,
    robots: list[Robot],
    tasks: list[Task] | None = None,
    plan: Plan | None = None,
):
    """Render starting positions, task locations, and planned assignment order."""
    tasks = tasks or []
    task_by_id = {task.id: task for task in tasks}
    owners = {a.task_id: a.robot_id for a in plan.assignments} if plan else {}
    palette = plt.get_cmap("tab10")
    colors = {robot.id: palette(i / max(len(robots), 1)) for i, robot in enumerate(robots)}
    fig, ax = plt.subplots(figsize=(9, 7))
    try:
        for obstacle in warehouse.obstacles:
            ax.add_patch(Rectangle(
                (obstacle.x - 0.5, obstacle.y - 0.5), 1, 1, color="#475569"
            ))

        for robot in robots:
            color = colors[robot.id]
            ax.scatter(robot.position.x, robot.position.y, s=180, color=color,
                       edgecolors="black", zorder=4, label=robot.id)
            ax.annotate(robot.id, (robot.position.x, robot.position.y),
                        xytext=(6, 9), textcoords="offset points")
            if plan:
                stops = [robot.position] + [
                    task_by_id[a.task_id].position
                    for a in plan.assignments if a.robot_id == robot.id
                ]
                ax.plot([p.x for p in stops], [p.y for p in stops],
                        color=color, linestyle="--", alpha=0.7, zorder=2)

        for task in tasks:
            color = colors.get(owners.get(task.id), "#64748b")
            ax.scatter(task.position.x, task.position.y, marker="X", s=130,
                       color=color, edgecolors="black", zorder=3)
            ax.annotate(task.id, (task.position.x, task.position.y),
                        xytext=(6, -14), textcoords="offset points")

        ax.set(xlim=(-0.5, warehouse.width - 0.5),
               ylim=(-0.5, warehouse.height - 0.5), xlabel="X", ylabel="Y",
               title="Warehouse and robot assignments", aspect="equal")
        ax.set_xticks(range(warehouse.width))
        ax.set_yticks(range(warehouse.height))
        ax.grid(alpha=0.2)
        if robots:
            ax.legend(title="Robots", loc="upper left", bbox_to_anchor=(1.02, 1))
        fig.tight_layout()
        st.pyplot(fig)
    finally:
        plt.close(fig)
    st.caption("Circles: robot starting positions. Crosses: tasks. Dark cells: obstacles. "
               "Dashed lines show assignment order using straight-line travel; "
               "obstacle avoidance and robot motion are not simulated yet.")
