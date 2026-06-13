""""""

from datetime import datetime

import reflex as rx

from lemonade_stand.ui.components.charts import budget_chart
from lemonade_stand.ui.components.date_picker import date_picker
from lemonade_stand.ui.components.stats import stats_grid
from lemonade_stand.ui.states.home_state import BudgetHealthStats
from lemonade_stand.ui.states.home_state import HomeState
from lemonade_stand.ui.states.ui_state import ActivityState


def quick_actions_panel(
    open_add_expense_modal: rx.event.EventType,
    open_add_budget_modal: rx.event.EventType,
    open_add_budget_allocations: rx.event.EventType,
) -> rx.Component:
    """"""

    def action_button(
        label: str, icon: str, on_click: rx.event.EventType, color: str = "indigo"
    ) -> rx.Component:
        """"""

        return rx.el.button(
            rx.el.div(
                rx.icon(
                    icon,
                    size=20,
                    class_name=f"text-{color}-600 dark:text-{color}-400 mb-2 group-hover:scale-110 transition-transform",
                ),
                rx.el.span(
                    label,
                    class_name="text-xs font-semibold text-gray-700 dark:text-gray-300",
                ),
                class_name="flex flex-col items-center justify-center p-4 bg-white dark:bg-gray-800/50 rounded-xl border border-gray-100 dark:border-gray-700/50 shadow-sm hover:shadow-md transition-all duration-300 hover:-translate-y-1 w-full h-full group",
            ),
            on_click=on_click,
            class_name="w-full",
        )

    return rx.el.div(
        rx.el.div(
            action_button(
                "New Expense",
                "receipt",
                open_add_expense_modal,
                "blue",
            ),
            action_button("New Budget", "wallet", open_add_budget_modal, "emerald"),
            action_button(
                "Budget Allocations",
                "clipboard_pen_line",
                open_add_budget_allocations,
                "purple",
            ),
            action_button("User Info", "users", rx.redirect("/user_info"), "orange"),
            class_name="grid grid-cols-2 sm:grid-cols-4 gap-4",
        ),
        class_name="mb-8 animate-in fade-in slide-in-from-bottom-4 duration-700",
    )


def activity_feed() -> rx.Component:
    """"""
    return rx.el.div(
        rx.el.div(
            rx.el.h3(
                "Recent Activity",
                class_name="text-lg font-bold text-gray-900 dark:text-gray-100",
            ),
            rx.el.select(
                rx.el.option("All", value="All"),
                rx.el.option("Expenses", value="Expense"),
                rx.el.option("Budgets", value="Budget"),
                rx.el.option("System", value="System"),
                rx.el.option("Warnings", value="Warning"),
                value=ActivityState.activity_filter,
                on_change=ActivityState.set_activity_filter,
                class_name="text-xs font-medium text-gray-600 dark:text-gray-400 bg-gray-50 dark:bg-gray-800 border-none rounded-lg focus:ring-1 focus:ring-indigo-500 py-1 pl-2 pr-8 cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors",
            ),
            class_name="flex items-center justify-between mb-6",
        ),
        class_name="bg-white/70 dark:bg-gray-800/50 backdrop-blur-xl p-6 rounded-2xl border border-white/50 dark:border-gray-700/50 shadow-[0_8px_30px_rgb(0,0,0,0.04)] h-full",
    )


def budget_health_widget() -> rx.Component:
    """"""

    def budget_health_row(budget: BudgetHealthStats) -> rx.Component:
        """"""
        return rx.el.div(
            rx.el.div(
                rx.el.span(
                    budget.category,
                    class_name="text-sm font-semibold text-gray-900 dark:text-gray-100 w-32 truncate",
                ),
                rx.el.div(
                    rx.el.div(
                        class_name=f"h-2 rounded-full {budget.progress_color}",
                        style={"width": f"{budget.utilization}%"},
                    ),
                    class_name="flex-1 h-2 bg-gray-100 dark:bg-gray-700 rounded-full overflow-hidden mx-3",
                ),
                rx.el.div(
                    rx.el.span(
                        f"{budget.utilization}%",
                        class_name="text-xs font-bold text-gray-700 dark:text-gray-300 w-12 text-right mr-3",
                    ),
                    rx.el.span(
                        rx.cond(
                            budget.utilization > 90,
                            "Critical",
                            rx.cond(budget.utilization > 75, "Warning", "Healthy"),
                        ),
                        class_name=f"""text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full w-20 text-center
                        {
                            rx.cond(
                                budget.utilization > 90,
                                "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400",
                                rx.cond(
                                    budget.utilization > 75,
                                    "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400",
                                    "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400",
                                ),
                            )
                        }""",
                    ),
                    class_name="flex items-center",
                ),
                class_name="flex items-center",
            ),
            class_name="py-3 border-b border-gray-50 dark:border-gray-700/50 last:border-0 hover:bg-white/50 dark:hover:bg-gray-700/30 transition-colors px-2 rounded-lg",
        )

    return rx.el.div(
        rx.el.div(
            rx.el.h3(
                "Budget Health Overview",
                class_name="text-lg font-bold text-gray-900 dark:text-gray-100",
            ),
            rx.el.a(
                "Manage",
                href="/budgets",
                class_name="text-sm font-medium text-indigo-600 dark:text-cyan-400 hover:text-indigo-800 transition-colors",
            ),
            class_name="flex items-center justify-between mb-4",
        ),
        rx.el.div(
            rx.foreach(HomeState.budget_health_stats, budget_health_row),
            class_name="flex flex-col max-h-[300px] overflow-y-auto custom-scrollbar pr-2",
        ),
        class_name="bg-white/70 dark:bg-gray-800/50 backdrop-blur-xl p-6 rounded-2xl border border-white/50 dark:border-gray-700/50 shadow-[0_8px_30px_rgb(0,0,0,0.04)] h-full",
    )


def home_content() -> rx.Component:
    """
    Home content page
    """

    def str_date_now(time_now: datetime | None = None) -> str:
        """ """
        time_now = datetime.now() if time_now is None else time_now

        if 11 <= time_now.day <= 13:
            str_day = f"{time_now.day}th"
        str_day = f"{time_now.day}" + {1: "st", 2: "nd", 3: "rd"}.get(
            time_now.day % 10, "th"
        )

        return time_now.strftime(f"%B {str_day}, %Y")

    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.h2(
                    "Overview",
                    class_name="font-['Raleway'] text-3xl font-bold text-gray-900 dark:text-gray-100 mb-2",
                ),
                date_picker(),
                class_name="flex justify-between items-center w-full",
            ),
            rx.el.p(
                f"Today is {str_date_now()}",
                class_name="text-gray-600 dark:text-gray-400 mb-6",
            ),
            class_name="mb-9 animate-in fade-in slide-in-from-bottom-4 duration-700",
        ),
        quick_actions_panel(
            open_add_expense_modal=HomeState.open_add_expense_modal,
            open_add_budget_modal=HomeState.open_add_budget_modal,
            open_add_budget_allocations=HomeState.open_add_budget_allocations,
        ),
        rx.el.div(
            stats_grid(
                total_earnings=HomeState.total_earnings,
                total_expenses=HomeState.total_expenses,
                remaining_earnings=HomeState.remaining_earnings,
                utilization_pct=HomeState.utilization_percentage,
            ),
            class_name="mb-8 animate-in fade-in slide-in-from-bottom-6 duration-700 delay-100",
        ),
        rx.el.div(
            rx.el.div(
                budget_chart(display_data=HomeState.budget_vs_actual_spend),
                class_name="lg:col-span-2",
            ),
            rx.el.div(activity_feed(), class_name="lg:col-span-1"),
            class_name="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6 animate-in fade-in slide-in-from-bottom-8 duration-700 delay-200",
        ),
        rx.el.div(
            rx.el.div(
                budget_health_widget(),
                class_name="lg:col-span-2",
            ),
            # rx.el.div(goals_widget(), class_name="lg:col-span-1"),
            class_name="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8 animate-in fade-in slide-in-from-bottom-8 duration-700 delay-200",
        ),
        class_name="max-w-7xl mx-auto relative z-10",
    )
