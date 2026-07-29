""" """

import datetime
import json
from dataclasses import dataclass
from dataclasses import field

from lemonade_stand.config.paths import AppPaths
from lemonade_stand.utils import set_up_logger

LOGGER = set_up_logger(__name__)
UI_DIR = AppPaths().ui_dir


@dataclass
class UserGoal:
    """Class representing a user's goal."""

    id: str = ""
    name: str = ""
    target_amount: float = 0.0
    current_amount: float = 0.0
    progress: float = 0.0
    deadline: str = datetime.date.today().isoformat()
    category: str = "General"
    status: str = "On Track"
    notes: str = ""


@dataclass
class AllGoals:
    """Class representing all goals."""

    goals: list[UserGoal] = field(default_factory=list)

    def load_goals(self) -> list[UserGoal]:
        """Load user goals from a JSON file."""

        config_path = UI_DIR / "user_goals.json"

        if config_path.exists():
            with config_path.open("r") as file:
                goals_data = json.load(file)
                return [UserGoal(**goal) for goal in goals_data]
        else:
            LOGGER.info("Goals file not found. Returning empty list.")
            return []

    def save_goals(self):
        """Saves the user goals to a JSON file"""

        config_path = UI_DIR / "user_goals.json"
        config_path.parent.mkdir(parents=True, exist_ok=True)

        with config_path.open("w") as file:
            json.dump([goal.__dict__ for goal in self.goals], file, indent=4)

            LOGGER.info("User goals saved to: \n\t%s", config_path)

    def delete_goal(self, id: str):
        """Deletes a goal by its ID"""
        self.goals = [x for x in self.goals if x.id != id]
        self.save_goals()

    def add_goal(self, **kwargs):
        """Adds a new goal to the goals data"""

        new_id = (
            str(len(self.goals) + 1) if kwargs.get("id", "") == "" else kwargs["id"]
        )
        progress = (
            0
            if kwargs["target_amount"] <= 0
            else ((kwargs["current_amount"] / kwargs["target_amount"]) * 100)
        )

        if progress == 100:
            status = "Completed"
        elif progress >= 50:
            status = "On Track"
        else:
            status = "At Risk"

        if new_id in [goal.id for goal in self.goals]:
            LOGGER.warning(
                "Goal with ID %s already exists. Overwriting addition.", new_id
            )
            goal_args = {
                "id": new_id,
            }
        else:
            goal_args = {"id": new_id, "progress": progress, "status": status}

        mappings = {**kwargs, **goal_args}
        self.goals = [
            UserGoal(
                id=str(mappings["id"]),
                name=str(mappings["name"]),
                target_amount=float(mappings["target_amount"]),
                current_amount=float(mappings["current_amount"]),
                progress=float(mappings["progress"]),
                deadline=str(mappings["deadline"]),
                category=str(mappings["category"]),
                status=str(mappings["status"]),
                notes=str(mappings["notes"]),
            )
        ] + [x for x in self.goals if x.id != new_id]

        self.save_goals()
