"""State for managing user goals."""

import typing

import reflex as rx

from lemonade_stand.ui.states.data_state import DataState
from lemonade_stand.ui.utils import AllGoals
from lemonade_stand.ui.utils import Allocations
from lemonade_stand.ui.utils import UserGoal
from lemonade_stand.utils import set_up_logger

LOGGER = set_up_logger(__name__)
STROKE_COLORS = [
    "#3B82F6",  # Blue 500
    "#10B981",  # Emerald 500
    "#F59E0B",  # Amber 500
    "#EC4899",  # Pink 500
    "#8B5CF6",  # Violet 500
    "#06B6D4",  # Cyan 500
    "#EF4444",  # Red 500
    "#84CC16",  # Lime 500
    "#F97316",  # Orange 500
    "#14B8A6",  # Teal 500
    "#6366F1",  # Indigo 500
    "#F43F5E",  # Rose 500
    "#EAB308",  # Yellow 500
    "#0EA5E9",  # Sky 500
    "#D946EF",  # Fuchsia 500
    "#A855F7",  # Purple 500
    "#22C55E",  # Green 500
    "#64748B",  # Slate 500
    "#78716C",  # Stone 500
    "#94A3B8",  # Slate 400
]


class GoalState(DataState):
    """State for managing savings goals and targets."""

    is_modal_open: bool = False
    current_goal: UserGoal = UserGoal()
    goals_obj: AllGoals = AllGoals()

    new_category_name: str = ""
    new_allocation_amount: str | int | float = ""

    @rx.var
    def goals(self) -> list[UserGoal]:
        """Return the list of goals."""
        return self.goals_obj.load_goals()

    @rx.var
    def expense_allocations(self) -> list[dict[str, typing.Any]]:
        """Return the allocations for expenses."""
        if "expenses" not in self.allocations:
            return []
        return self.allocations["expenses"].as_dicts

    @rx.var
    def total_budget_amount(self) -> int | float:
        """Return the total budget amount."""
        return sum(x["allocated_amount"] for x in self.expense_allocations)

    @rx.var
    def total_budget_count(self) -> int:
        """Return the total number of budgets."""
        return len(self.expense_allocations)

    @rx.var
    def good_budget_count(self) -> int:
        """Return the number of good standing budgets."""
        return len([x for x in self.expense_allocations if x["progress"] < 75])

    @rx.var
    def at_risk_budget_count(self) -> int:
        """Return the number of at-risk budgets."""
        return len([x for x in self.expense_allocations if x["progress"] >= 90])

    @rx.var
    def budget_distribution_data(self) -> list[dict]:
        """Return the budget distribution data."""
        return [
            {
                "name": row["category"],
                "clean_name": row["category"].replace(" ", "_"),
                "percent_label": f"{row['progress']}%",
                "amount": row["allocated_amount"],
                "fill": STROKE_COLORS[index % len(STROKE_COLORS)],
                "stroke": STROKE_COLORS[index % len(STROKE_COLORS)],
                "type": "monotone",
            }
            for index, row in enumerate(self.expense_allocations)
        ]

    @rx.event
    def open_add_modal(self):
        """Open the add goal modal with default values."""
        self.current_goal = UserGoal()
        self.is_modal_open = True

    @rx.event
    def open_edit_modal(self, goal: UserGoal):
        """Open the edit goal modal with the specified goal."""
        self.current_goal = goal
        self.is_modal_open = True

    @rx.event
    def close_modal(self):
        """Close the add/edit goal modal."""
        self.is_modal_open = False

    @rx.event
    def update_current_goal(self, key: str, value: str):
        """Update a field in the current goal."""
        if key in ["target_amount", "current_amount"]:
            setattr(self.current_goal, key, float(value))
        else:
            setattr(self.current_goal, key, value)

    @rx.event
    def save_goal(self):
        """Save the current goal, either updating an existing one or adding a new one."""
        self.goals_obj.add_goal(**self.current_goal.__dict__)
        self.close_modal()

    @rx.event
    def delete_goal(self, id: str):
        """Delete a goal by its ID."""
        self.goals_obj.delete_goal(id)

    @rx.event
    def set_allocation_update(
        self, category_type: str, new_category: str, new_amount: str | int | float
    ):
        """Updates a specific allocation setting."""
        curr_updates = self.allocation_updates.get(category_type, ("", ""))

        self.new_category_name = new_category if new_category != "" else curr_updates[0]
        self.new_allocation_amount = new_amount if new_amount != "" else curr_updates[1]
        self.allocation_updates[category_type] = (
            self.new_category_name,
            float(self.new_allocation_amount),
        )

    @rx.event
    def add_new_allocation(self, category_type: str):
        """Adds a new allocation entry under the specified category."""
        if category_type in self.allocation_updates:
            updates = self.allocation_updates[category_type]

            if category_type not in self.allocations:
                self.allocations[category_type] = Allocations(
                    name=category_type, _transaction_df=self.shared_data.expenses
                )

            self.allocations[category_type].add_allocation(
                category=updates[0], allocated_amount=float(updates[1])
            )
            self.allocations = self.allocations

            # Reset the allocation update after adding
            self.allocation_updates = {
                k: v for k, v in self.allocation_updates.items() if k != category_type
            }

            self.new_category_name = ""
            self.new_allocation_amount = ""
