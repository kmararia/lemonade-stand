"""State for managing user goals."""

import typing

import reflex as rx

from lemonade_stand.ui.states.data_state import DataState
from lemonade_stand.ui.utils import AllGoals
from lemonade_stand.ui.utils import Allocations
from lemonade_stand.ui.utils import UserGoal
from lemonade_stand.utils import set_up_logger

LOGGER = set_up_logger(__name__)


class GoalState(DataState):
    """State for managing savings goals and targets."""

    is_modal_open: bool = False
    current_goal: UserGoal = UserGoal()
    goals_obj: AllGoals = AllGoals()

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
        self, category_type: str, new_category: str, new_amount: float
    ):
        """Updates a specific allocation setting."""
        curr_updates = self.allocation_updates.get(category_type, ("", 0.0))
        self.allocation_updates[category_type] = (
            new_category if new_category != "" else curr_updates[0],
            new_amount if float(new_amount) != 0.0 else curr_updates[1],
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

            # Reset the allocation update after adding
            self.allocation_updates = {
                k: v for k, v in self.allocation_updates.items() if k != category_type
            }
