
from models import Warehouse, Robot, Position
from Ai_parser import OpenAIMissionParser
from mission_service import MissionService


warehouse = Warehouse(width=10, height=10)

robots = [
    Robot(id="R1", position=Position(x=0, y=0)),
    Robot(id="R2", position=Position(x=9, y=0)),
    Robot(id="R3", position=Position(x=0, y=9)),
    Robot(id="R4", position=Position(x=9, y=9)),
]

service = MissionService(OpenAIMissionParser())

mission, plan = service.create_plan(
    (
        "Inspect the loading dock, storage shelves, "
        "emergency exits, and maintenance area. "
        "The loading dock is the highest priority."
    ),
    warehouse,
    robots
)

print("\nGENERATED MISSION")
print(mission.model_dump_json(indent=2))

print("\nTASK ALLOCATION")
print(plan.model_dump_json(indent=2))
