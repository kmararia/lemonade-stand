"""Goals page."""

import typing

import reflex as rx

from lemonade_stand.ui.components.layout import page_layout
from lemonade_stand.ui.states.goals_state import GoalState
from lemonade_stand.ui.states.goals_state import UserGoal


def budgets_widget() -> rx.Component:
    """Full-width budget tracker with an inline add row."""

    def budget_stat_item(
        label: str, value: str, icon: str, icon_color: str = "--accent-color"
    ) -> rx.Component:
        """A thematic stat item for the Budgets widget."""

        return rx.el.div(
            rx.el.div(
                rx.icon(
                    icon, size=22, class_name=f"text-[var({icon_color})] m-2 opacity-80"
                ),
                rx.el.span(
                    value, class_name="text-xl font-bold text-[var(--text-main)]"
                ),
                class_name="flex flex-col items-center justify-center p-3 rounded-xl bg-[var(--bg-subtle)] w-full",
            ),
            rx.el.span(
                label,
                class_name="text-xs font-medium text-[var(--text-muted)] mt-2 text-center block uppercase tracking-wider",
            ),
            class_name="flex flex-col items-center flex-1",
        )

    def budget_row_item(budget: dict) -> rx.Component:
        """A single row representing an active budget."""

        progress_color = rx.cond(
            budget["progress"].to(int) >= 90,
            "bg-[var(--critical-text)]",
            rx.cond(
                budget["progress"].to(int) >= 75,
                "bg-[var(--warning-text)]",
                "bg-[var(--healthy-text)]",
            ),
        )

        return rx.el.div(
            rx.el.div(
                rx.el.span(
                    budget["category"],
                    class_name="text-sm font-semibold text-[var(--text-main)] truncate mb-3",
                ),
                rx.el.div(
                    rx.el.div(
                        rx.el.div(
                            class_name=f"h-1.5 rounded-full {progress_color} transition-all duration-1000",
                            style={"width": f"{budget['progress'].to(int):.0f}%"},
                        ),
                        class_name="w-full h-1.5 bg-[var(--bg-subtle)] rounded-full overflow-hidden",
                    ),
                    rx.el.span(
                        f"${budget['transaction_amount'].to(float):,.0f} / ${budget['allocated_amount'].to(float):,.0f}",
                        class_name="text-xs font-medium text-[var(--text-muted)] w-32 text-right shrink-0 mr-3 whitespace-nowrap",
                    ),
                    class_name="flex justify-between items-end",
                ),
                class_name="w-full",
            ),
            class_name="py-2 border-b border-[var(--border-subtle)] last:border-0",
        )

    return rx.el.div(
        rx.el.div(
            rx.el.h3(
                "Active Budgets", class_name="text-lg font-bold text-[var(--text-main)]"
            ),
            rx.icon("wallet", size=20, class_name="text-[var(--text-muted)]"),
            class_name="flex items-center justify-between mb-6",
        ),
        # Stats Row
        rx.el.div(
            budget_stat_item(
                "Total Budgets",
                f"${GoalState.total_budget_amount:,.0f}",
                "bar_chart_3",
                "--accent-color",
            ),
            budget_stat_item(
                "Active Budgets",
                f"{GoalState.total_budget_count:,.0f}",
                "eye",
                "--accent-color",
            ),
            budget_stat_item(
                "Good Standing",
                f"{GoalState.good_budget_count:,.0f}",
                "circle_check_big",
                "--healthy-text",
            ),
            budget_stat_item(
                "At Risk",
                f"{GoalState.at_risk_budget_count:,.0f}",
                "badge_alert",
                "--critical-text",
            ),
            class_name="flex gap-4 mb-6",
        ),
        # Budget Rows
        rx.el.div(
            rx.foreach(GoalState.expense_allocations, budget_row_item),
            class_name="flex flex-col mb-4 max-h-[280px] overflow-auto custom-scrollbar",
        ),
        # Quick Add Row
        rx.el.div(
            rx.el.input(
                placeholder="New budget name...",
                value=GoalState.new_category_name,
                on_change=lambda x: GoalState.set_allocation_update("expenses", x, ""),
                class_name="flex-1 bg-[var(--app-bg-inner)] border border-[var(--border-main)] rounded-lg px-4 py-2.5 text-sm text-[var(--text-main)] focus:border-[var(--accent-color)] outline-none shadow-sm",
            ),
            rx.el.input(
                type="number",
                placeholder="$ Amount",
                value=GoalState.new_allocation_amount,
                on_change=lambda x: GoalState.set_allocation_update("expenses", "", x),
                class_name="w-45 bg-[var(--app-bg-inner)] border border-[var(--border-main)] rounded-lg px-4 py-2.5 text-sm text-[var(--text-main)] focus:border-[var(--accent-color)] outline-none shadow-sm",
            ),
            rx.el.button(
                rx.icon("plus", size=20),
                on_click=lambda _: GoalState.add_new_allocation("expenses"),
                class_name="p-2.5 bg-[var(--accent-color)] text-[var(--app-bg-inner)] rounded-lg hover:opacity-90 transition-opacity cursor-pointer shadow-sm flex items-center justify-center",
            ),
            class_name="flex gap-3 items-center mt-2 pt-4 border-t border-[var(--border-subtle)]",
        ),
        class_name="bg-[var(--bg-card)] p-6 rounded-2xl border border-[var(--border-main)] shadow-sm w-full mb-10",
    )


def goal_card(goal: UserGoal) -> rx.Component:
    """Return a card component for the given goal."""

    def goal_status_badge(status: str) -> rx.Component:
        """Return a badge component for the given goal status."""

        return typing.cast(
            rx.Component,
            rx.match(
                status,
                (
                    "Completed",
                    rx.el.span(
                        "Completed",
                        class_name="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-500/10 text-emerald-500",
                    ),
                ),
                (
                    "On Track",
                    rx.el.span(
                        "On Track",
                        class_name="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold bg-blue-500/10 text-blue-500",
                    ),
                ),
                (
                    "At Risk",
                    rx.el.span(
                        "At Risk",
                        class_name="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold bg-orange-500/10 text-orange-500",
                    ),
                ),
                rx.el.span(
                    status,
                    class_name="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold bg-[var(--bg-subtle)] text-[var(--text-muted)]",
                ),
            ),
        )

    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.span(
                        goal.category,
                        class_name="text-xs font-semibold text-[var(--accent-color)] uppercase tracking-wider mb-1 block",
                    ),
                    rx.el.h3(
                        goal.name,
                        class_name="text-lg font-bold text-[var(--text-main)] line-clamp-1",
                    ),
                ),
                goal_status_badge(goal.status),
                class_name="flex justify-between items-start mb-4",
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.span(
                        "Progress",
                        class_name="text-xs font-medium text-[var(--text-muted)]",
                    ),
                    rx.el.span(
                        f"{goal.progress:.0f}%",
                        class_name="text-xs font-bold text-[var(--text-main)]",
                    ),
                    class_name="flex justify-between mb-2",
                ),
                rx.el.div(
                    rx.el.div(
                        class_name=rx.cond(
                            goal.status == "Completed",
                            "h-2 rounded-full bg-emerald-500 transition-all duration-1000",
                            rx.cond(
                                goal.status == "At Risk",
                                "h-2 rounded-full bg-orange-500 transition-all duration-1000",
                                "h-2 rounded-full bg-blue-500 transition-all duration-1000",
                            ),
                        ),
                        style={"width": f"{goal.progress}%"},
                    ),
                    class_name="w-full h-2 bg-[var(--bg-subtle)] rounded-full overflow-hidden mb-4",
                ),
                rx.el.div(
                    rx.el.div(
                        rx.el.p(
                            "Current",
                            class_name="text-xs text-[var(--text-muted)] font-medium",
                        ),
                        rx.el.p(
                            f"${goal.current_amount:,.0f}",
                            class_name="text-sm font-bold text-[var(--text-main)]",
                        ),
                    ),
                    rx.el.div(
                        rx.el.p(
                            "Target",
                            class_name="text-xs text-[var(--text-muted)] font-medium text-right",
                        ),
                        rx.el.p(
                            f"${goal.target_amount:,.0f}",
                            class_name="text-sm font-bold text-[var(--text-main)] text-right",
                        ),
                    ),
                    class_name="flex justify-between items-end",
                ),
                class_name="mb-6",
            ),
            rx.el.div(
                rx.el.div(
                    rx.icon(
                        "calendar",
                        size=14,
                        class_name="text-[var(--text-muted)] mr-2 shrink-0",
                    ),
                    rx.el.span(
                        f"Due {goal.deadline}",
                        class_name="text-xs text-[var(--text-muted)]",
                    ),
                    class_name="flex items-center",
                ),
                rx.el.div(
                    rx.el.button(
                        rx.icon("pencil", size=14),
                        on_click=lambda: GoalState.open_edit_modal(goal),
                        class_name="p-1.5 text-[var(--text-muted)] hover:text-[var(--text-main)] hover:bg-[var(--bg-subtle)] rounded-lg transition-colors mr-1 cursor-pointer",
                    ),
                    rx.el.button(
                        rx.icon("trash-2", size=14),
                        on_click=lambda: GoalState.delete_goal(goal.id),
                        class_name="p-1.5 text-[var(--text-muted)] hover:bg-red-500/10 hover:text-red-500 rounded-lg transition-colors cursor-pointer",
                    ),
                    class_name="flex items-center",
                ),
                class_name="flex justify-between items-center pt-4 border-t border-[var(--border-subtle)]",
            ),
        ),
        class_name="bg-[var(--bg-card)] p-6 rounded-2xl border border-[var(--border-main)] shadow-sm hover:shadow-md transition-all duration-300 hover:-translate-y-1",
    )


def goal_modal() -> rx.Component:
    """Modal for adding or editing a goal."""

    input_class = """
        text-[var(--text-main)] w-full rounded-lg shadow-sm
        bg-[var(--app-bg-inner)] border border-[var(--border-main)]
        focus:border-[var(--accent-color)] focus:ring-[var(--accent-color)] px-4 py-2
    """

    return rx.cond(
        GoalState.is_modal_open,
        rx.el.div(
            rx.el.div(
                class_name="fixed inset-0 bg-black/40 backdrop-blur-sm transition-opacity",
                on_click=GoalState.close_modal,
            ),
            rx.el.div(
                rx.el.h3(
                    rx.cond(GoalState.current_goal.id, "Edit Goal", "New Savings Goal"),
                    class_name="text-lg font-bold text-[var(--text-main)] mb-4",
                ),
                rx.el.div(
                    rx.el.div(
                        rx.el.label(
                            "Goal Name",
                            class_name="block text-sm font-medium text-[var(--text-main)] mb-1",
                        ),
                        rx.el.input(
                            default_value=GoalState.current_goal.name,
                            on_change=lambda v: GoalState.update_current_goal(
                                "name", v
                            ),
                            class_name=input_class,
                            placeholder="e.g. Emergency Fund",
                        ),
                        class_name="mb-4",
                    ),
                    rx.el.div(
                        rx.el.div(
                            rx.el.label(
                                "Target Amount",
                                class_name="block text-sm font-medium text-[var(--text-main)] mb-1",
                            ),
                            rx.el.input(
                                type="number",
                                default_value=GoalState.current_goal.target_amount,
                                on_change=lambda v: GoalState.update_current_goal(
                                    "target_amount", v
                                ),
                                class_name=input_class,
                            ),
                            class_name="col-span-1",
                        ),
                        rx.el.div(
                            rx.el.label(
                                "Current Saved",
                                class_name="block text-sm font-medium text-[var(--text-main)] mb-1",
                            ),
                            rx.el.input(
                                type="number",
                                default_value=GoalState.current_goal.current_amount,
                                on_change=lambda v: GoalState.update_current_goal(
                                    "current_amount", v
                                ),
                                class_name=input_class,
                            ),
                            class_name="col-span-1",
                        ),
                        class_name="grid grid-cols-2 gap-4 mb-4",
                    ),
                    rx.el.div(
                        rx.el.div(
                            rx.el.label(
                                "Category",
                                class_name="block text-sm font-medium text-[var(--text-main)] mb-1",
                            ),
                            rx.el.select(
                                rx.el.option("General", value="General"),
                                rx.el.option("Savings", value="Savings"),
                                rx.el.option("Income", value="Income"),
                                value=GoalState.current_goal.category,
                                on_change=lambda v: GoalState.update_current_goal(
                                    "category", v
                                ),
                                class_name=input_class,
                            ),
                            class_name="col-span-1",
                        ),
                        rx.el.div(
                            rx.el.label(
                                "Deadline",
                                class_name="block text-sm font-medium text-[var(--text-main)] mb-1",
                            ),
                            rx.el.input(
                                type="date",
                                default_value=GoalState.current_goal.deadline,
                                on_change=lambda v: GoalState.update_current_goal(
                                    "deadline", v
                                ),
                                class_name=input_class,
                            ),
                            class_name="col-span-1",
                        ),
                        class_name="grid grid-cols-2 gap-4 mb-4",
                    ),
                    rx.el.div(
                        rx.el.label(
                            "Status",
                            class_name="block text-sm font-medium text-[var(--text-main)] mb-1",
                        ),
                        rx.el.select(
                            rx.el.option("On Track", value="On Track"),
                            rx.el.option("At Risk", value="At Risk"),
                            rx.el.option("Completed", value="Completed"),
                            value=GoalState.current_goal.status,
                            on_change=lambda v: GoalState.update_current_goal(
                                "status", v
                            ),
                            class_name=input_class,
                        ),
                        class_name="mb-4",
                    ),
                    rx.el.div(
                        rx.el.label(
                            "Notes",
                            class_name="block text-sm font-medium text-[var(--text-main)] mb-1",
                        ),
                        rx.el.textarea(
                            default_value=GoalState.current_goal.notes,
                            on_change=lambda v: GoalState.update_current_goal(
                                "notes", v
                            ),
                            class_name=input_class,
                            rows="3",
                        ),
                        class_name="mb-6",
                    ),
                    rx.el.div(
                        rx.el.button(
                            "Cancel",
                            on_click=GoalState.close_modal,
                            class_name="""
                                px-4 py-2 mr-3 font-medium
                                text-sm text-[var(--text-main)] bg-[var(--bg-card)]
                                border border-[var(--border-main)] rounded-lg hover:bg-[var(--bg-subtle)]
                                transition-colors cursor-pointer
                            """,
                        ),
                        rx.el.button(
                            "Save Goal",
                            on_click=GoalState.save_goal,
                            class_name="""
                                px-4 py-2 text-sm font-medium text-[var(--app-bg-inner)]
                                bg-[var(--accent-color)] rounded-lg
                                hover:opacity-90 transition-opacity cursor-pointer
                            """,
                        ),
                        class_name="flex justify-end",
                    ),
                ),
                class_name="""
                relative bg-[var(--bg-card)] rounded-2xl shadow-2xl border border-[var(--border-main)]
                max-w-md w-full p-6 z-50 animate-in fade-in zoom-in duration-200
                """,
            ),
            class_name="fixed inset-0 z-50 flex items-center justify-center p-4",
        ),
        rx.el.div(),
    )


def goals_page() -> rx.Component:
    """Goals tracking page."""

    return page_layout(
        rx.el.div(
            # HEADER
            rx.el.div(
                rx.el.div(
                    rx.el.h2(
                        "Budgets & Goals",
                        class_name="text-2xl font-bold text-[var(--text-main)] tracking-tight mb-2",
                    ),
                    rx.el.p(
                        "Track your progress towards financial targets.",
                        class_name="text-sm text-[var(--text-muted)] mt-2",
                    ),
                ),
                class_name="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-10",
            ),
            # TOP HALF: BUDGETS
            rx.el.div(
                budgets_widget(),
                class_name="animate-in fade-in slide-in-from-bottom-4 duration-500",
            ),
            # BOTTOM HALF: GOALS
            rx.el.div(
                rx.el.h3(
                    "Your Goals",
                    class_name="text-lg font-bold text-[var(--text-main)] mb-6",
                ),
                rx.cond(
                    GoalState.goals.length() > 0,
                    rx.el.div(
                        rx.foreach(GoalState.goals, goal_card),
                        class_name="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6 animate-in fade-in slide-in-from-bottom-6 duration-700",
                    ),
                    rx.el.div(
                        rx.el.div(
                            rx.el.div(
                                rx.icon(
                                    "target",
                                    size=48,
                                    class_name="text-[var(--accent-color)] mx-auto opacity-80",
                                ),
                                class_name="w-24 h-24 bg-[var(--bg-subtle)] rounded-full flex items-center justify-center mx-auto mb-6",
                            ),
                            rx.el.h3(
                                "No goals yet",
                                class_name="text-xl font-bold text-[var(--text-main)] mb-2",
                            ),
                            rx.el.p(
                                "Set financial targets to track your savings/income progress and achievements.",
                                class_name="text-[var(--text-muted)] mb-8 max-w-md mx-auto",
                            ),
                            rx.el.button(
                                rx.icon("plus", size=18, class_name="mr-2"),
                                "Set First Goal",
                                on_click=GoalState.open_add_modal,
                                class_name="""
                                    inline-flex items-center px-5 py-2.5 font-semibold text-sm
                                    bg-[var(--accent-color)] text-[var(--app-bg-inner)] rounded-xl
                                    hover:opacity-90 transition-all shadow-md hover:shadow-lg hover:-translate-y-0.5 cursor-pointer
                                """,
                            ),
                            class_name="text-center py-12 px-4",
                        ),
                        class_name="""
                            bg-[var(--bg-card)] rounded-3xl border-2 border-dashed border-[var(--border-main)]
                            flex flex-col items-center justify-center min-h-[400px] w-full
                            animate-in fade-in zoom-in duration-500
                        """,
                    ),
                ),
            ),
            # FLOATING ADD GOAL BUTTON & MODAL
            goal_modal(),
            rx.el.div(
                rx.el.button(
                    rx.icon("plus", size=22),
                    on_click=GoalState.open_add_modal,
                    class_name="""
                        w-10 h-10 bg-[var(--accent-color)] text-[var(--app-bg-inner)] rounded-full shadow-lg
                        flex items-center justify-center hover:scale-110 active:scale-95
                        transition-all duration-300 animate-bounce-in cursor-pointer
                        pointer-events-auto
                    """,
                    title="Add New Goal",
                ),
                class_name="w-full flex justify-center mt-12 pb-10 z-10",
            ),
            class_name="w-full mx-auto relative z-10",
        ),
    )
