
from pydantic import BaseModel, Field, model_validator


class Position(BaseModel):
    x: int = Field(ge=0)
    y: int = Field(ge=0)



class Robot(BaseModel):
    id: str = Field(min_length=1)
    position: Position
    speed: float = Field(default=1.0, gt=0)


class Task(BaseModel):
    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    position: Position
    priority: int = Field(ge=1, le=5)
    duration: float = Field(default=2.0, ge=0)



class Warehouse(BaseModel):
    width: int = Field(gt=0)
    height: int = Field(gt=0)
    obstacles: list[Position] = Field(default_factory=list)

    def contains(self, position: Position) -> bool:
        return (
            0 <= position.x < self.width
            and 0 <= position.y < self.height
        )

    def is_blocked(self, position: Position) -> bool:
        return position in self.obstacles

    @model_validator(mode="after")
    def validate_obstacles(self):
        for obstacle in self.obstacles:
            if not self.contains(obstacle):
                raise ValueError(
                    "Obstacle is outside the warehouse"
                )
        return self


class Mission(BaseModel):
    id: str = Field(min_length=1)
    objective: str = Field(min_length=1)
    warehouse: Warehouse
    robots: list[Robot] = Field(min_length=1)
    tasks: list[Task] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_mission(self):
        robot_ids = [r.id for r in self.robots]
        task_ids = [t.id for t in self.tasks]

        if len(robot_ids) != len(set(robot_ids)):
            raise ValueError("Duplicate robot IDs")

        if len(task_ids) != len(set(task_ids)):
            raise ValueError("Duplicate task IDs")

        for item in [*self.robots, *self.tasks]:
            if not self.warehouse.contains(item.position):
                raise ValueError(
                    f"{item.id} is outside the warehouse"
                )

            if self.warehouse.is_blocked(item.position):
                raise ValueError(
                    f"{item.id} is on an obstacle"
                )

        return self
