"""Run with: python -m streamlit run app.py."""

import os

import streamlit as st
from openai import OpenAIError

from Ai_parser import OpenAIMissionParser
from mission_service import MissionService
from models import Position, Robot, Warehouse
from visualizer import visualize_warehouse


def main():
    st.set_page_config(page_title="SwarmPlanner", layout="wide")
    st.title("SwarmPlanner")
    st.write("Describe an inspection mission and assign tasks to your warehouse robots.")

    with st.sidebar:
        st.header("Warehouse setup")
        width = st.number_input("Width (cells)", min_value=2, max_value=50, value=10)
        height = st.number_input("Height (cells)", min_value=2, max_value=50, value=10)
        count = st.slider("Number of robots", min_value=1, max_value=8, value=4)
        speed = st.number_input("Robot speed (cells/minute)", min_value=0.1, value=1.0)

    # Spread robots evenly around the perimeter without duplicate starting cells.
    perimeter = (
        [(x, 0) for x in range(width)]
        + [(width - 1, y) for y in range(1, height)]
        + [(x, height - 1) for x in range(width - 2, -1, -1)]
        + [(0, y) for y in range(height - 2, 0, -1)]
    )
    if count > len(perimeter):
        st.warning("Increase warehouse dimensions to fit all robots.")
        return
    warehouse = Warehouse(width=width, height=height)
    robots = [
        Robot(id=f"R{i + 1}", position=Position(
            x=perimeter[i * len(perimeter) // count][0],
            y=perimeter[i * len(perimeter) // count][1],
        ), speed=speed)
        for i in range(count)
    ]
    setup = (width, height, count, speed)
    if st.session_state.get("setup") != setup:
        st.session_state.pop("result", None)
        st.session_state["setup"] = setup

    with st.form("mission"):
        prompt = st.text_area("Mission description", value=(
            "Inspect the loading dock, storage shelves, emergency exits, and "
            "maintenance area. The loading dock is the highest priority."
        ))
        submitted = st.form_submit_button("Generate plan")

    if submitted:
        st.session_state.pop("result", None)
        if not prompt.strip():
            st.error("Enter a mission description.")
        elif not os.getenv("OPENAI_API_KEY"):
            st.error("Set OPENAI_API_KEY in your .env file before generating a plan.")
        else:
            try:
                with st.spinner("Creating mission and assigning tasks..."):
                    service = MissionService(OpenAIMissionParser())
                    st.session_state["result"] = service.create_plan(prompt, warehouse, robots)
            except (ValueError, OpenAIError) as exc:
                st.error(f"Could not generate a plan: {exc}")

    result = st.session_state.get("result")
    if result:
        mission, plan = result
        st.subheader(mission.objective)
        time_col, distance_col = st.columns(2)
        time_col.metric("Estimated completion (minutes)", f"{plan.makespan:.2f}")
        distance_col.metric("Total travel (cells)", f"{plan.total_distance:.2f}")
        visualize_warehouse(mission.warehouse, mission.robots, mission.tasks, plan)
        tasks = {task.id: task for task in mission.tasks}
        st.subheader("Task assignments")
        st.dataframe([
            {"Task": a.task_id, "Name": tasks[a.task_id].name,
             "Robot": a.robot_id, "Priority": tasks[a.task_id].priority,
             "Start (min)": round(a.start_time, 2),
             "Finish (min)": round(a.finish_time, 2)}
            for a in plan.assignments
        ], hide_index=True)
        st.caption("Start time includes travel to the task. AI-generated locations are illustrative.")
    else:
        visualize_warehouse(warehouse, robots)


if __name__ == "__main__":
    main()
