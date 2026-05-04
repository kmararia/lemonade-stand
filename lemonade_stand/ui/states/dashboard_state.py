""""""

import reflex as rx

from lemonade_stand.ui.states.budget_state import BudgetState


class DashboardState(rx.State):
    """State for managing dashboard specific insights and alerts."""

    @rx.var
    async def spending_insights(self) -> list[str]:
        """Returns AI-like spending recommendations."""
        bs = await self.get_state(BudgetState)
        insights = []
        if bs.total_spent > bs.total_budget * 0.8:
            insights.append(
                "Spending velocity is high. Consider freezing non-essential expenses."
            )
        pending_count = len(
            [e for e in bs.expenses if e["approval_status"] == "Pending"]
        )
        if pending_count > 5:
            insights.append(
                f"You have {pending_count} pending approvals. Clearing these will update accurate spend data."
            )
        if bs.category_distribution:
            top_cat = max(bs.category_distribution, key=lambda x: x["value"])
            insights.append(
                f"{top_cat['name']} accounts for the largest share of expenses. Review mainly recurring costs there."
            )
        if not insights:
            insights.append("Budget health looks good. Keep tracking expenses daily.")
        return insights


class ActivityState(rx.State):
    """"""

    activity_filter: str = "All"

    @rx.event
    def set_activity_filter(self, value: str):
        """Change the activity filter value."""
        self.activity_filter = value
