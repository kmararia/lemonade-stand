""""""

import datetime
import logging
import uuid
from typing import TypedDict

import reflex as rx


class Goal(TypedDict):
    """"""

    id: str
    name: str
    target_amount: float
    current_amount: float
    deadline: str
    category: str
    status: str
    notes: str


class GoalsState(rx.State):
    """State for managing savings goals and targets."""

    is_modal_open: bool = False
    current_goal: Goal = {
        "id": "",
        "name": "",
        "target_amount": 0.0,
        "current_amount": 0.0,
        "deadline": datetime.date.today().isoformat(),
        "category": "General",
        "status": "On Track",
        "notes": "",
    }
    goals: list[Goal] = [
        {
            "id": "g1",
            "name": "Emergency Fund",
            "target_amount": 20000.0,
            "current_amount": 15000.0,
            "deadline": "2024-12-31",
            "category": "Savings",
            "status": "On Track",
            "notes": "3 months of operating expenses",
        },
        {
            "id": "g2",
            "name": "New Office Equipment",
            "target_amount": 5000.0,
            "current_amount": 1200.0,
            "deadline": "2024-06-30",
            "category": "Equipment",
            "status": "At Risk",
            "notes": "Laptops and monitors for new hires",
        },
        {
            "id": "g3",
            "name": "Team Retreat",
            "target_amount": 10000.0,
            "current_amount": 10000.0,
            "deadline": "2024-08-15",
            "category": "Events",
            "status": "Completed",
            "notes": "Annual summer gathering",
        },
        {
            "id": "g4",
            "name": "Software Migration",
            "target_amount": 8000.0,
            "current_amount": 3500.0,
            "deadline": "2024-09-01",
            "category": "Technology",
            "status": "On Track",
            "notes": "Moving to new CRM",
        },
    ]

    @rx.event
    def open_add_modal(self):
        """"""

        self.current_goal = {
            "id": "",
            "name": "",
            "target_amount": 0.0,
            "current_amount": 0.0,
            "deadline": datetime.date.today().isoformat(),
            "category": "General",
            "status": "On Track",
            "notes": "",
        }
        self.is_modal_open = True

    @rx.event
    def open_edit_modal(self, goal: Goal):
        """"""

        self.current_goal = goal
        self.is_modal_open = True

    @rx.event
    def close_modal(self):
        """"""

        self.is_modal_open = False

    @rx.event
    def update_current_goal(self, key: str, value: str):
        """"""

        if key in ["target_amount", "current_amount"]:
            try:
                self.current_goal[key] = float(value)
            except ValueError as e:
                logging.exception("Error updating goal %s: %s", key, e)
        else:
            self.current_goal[key] = value

    @rx.var
    def total_goals_count(self) -> int:
        """"""

        return len(self.goals)

    @rx.var
    def completed_goals_count(self) -> int:
        """"""

        return len([g for g in self.goals if g["status"] == "Completed"])

    @rx.var
    def at_risk_goals_count(self) -> int:
        """"""

        return len([g for g in self.goals if g["status"] == "At Risk"])

    @rx.var
    def dashboard_goals(self) -> list[Goal]:
        """"""

        active = [g for g in self.goals if g["status"] != "Completed"]
        completed = [g for g in self.goals if g["status"] == "Completed"]
        return (active + completed)[:3]

    @rx.event
    async def save_goal(self):
        """"""

        if not self.current_goal["name"]:
            return

        if self.current_goal["status"] != "Completed" and (
            self.current_goal["target_amount"] > 0
            and self.current_goal["current_amount"]
            >= self.current_goal["target_amount"]
        ):
            self.current_goal["status"] = "Completed"
        if self.current_goal["id"]:
            self.goals = [
                g if g["id"] != self.current_goal["id"] else self.current_goal
                for g in self.goals
            ]
        else:
            new_goal = self.current_goal.copy()
            new_goal["id"] = str(uuid.uuid4())
            self.goals.append(new_goal)
        self.close_modal()

    @rx.event
    async def delete_goal(self, id: str):
        """"""

        goal = next((g for g in self.goals if g["id"] == id), None)
        if goal:
            pass
        self.goals = [g for g in self.goals if g["id"] != id]
