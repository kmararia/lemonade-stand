""""""

from datetime import datetime
from decimal import Decimal

import reflex as rx

from lemonade_stand.ui.components.charts import budget_chart
from lemonade_stand.ui.components.date_picker import date_picker
from lemonade_stand.ui.components.small_cards import stats_card
from lemonade_stand.ui.components.widgets import activity_feed
from lemonade_stand.ui.components.widgets import budget_health_widget
from lemonade_stand.ui.components.widgets import category_distribution_widget
from lemonade_stand.ui.states.expense_state import ExpenseState
from lemonade_stand.ui.states.home_state import HomeState
from lemonade_stand.ui.states.income_state import IncomeState


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
            class_name="grid grid-cols-2 sm:grid-cols-4 gap-5",
        ),
        class_name="mb-5 animate-in fade-in slide-in-from-bottom-4 duration-700",
    )


def stats_grid(
    total_earnings: rx.Var[int | float | Decimal],
    total_expenses: rx.Var[int | float | Decimal],
    remaining_earnings: rx.Var[int | float | Decimal],
    utilization_pct: rx.Var[int | float | Decimal],
) -> rx.Component:
    """"""

    return rx.el.div(
        stats_card(
            "Total Earnings",
            f"${total_earnings:,.0f}",
            "wallet",
            trend="+12% from last Q",
            color="blue",
            trend_up=True,
        ),
        stats_card(
            "Total Spent",
            f"${total_expenses:,.0f}",
            "credit-card",
            trend="+5% vs target",
            color="indigo",
            trend_up=False,
        ),
        stats_card(
            "Remaining Earnings",
            f"${remaining_earnings:,.0f}",
            "piggy-bank",
            color="indigo",
            progress=utilization_pct,
        ),
        stats_card(
            "Utilization",
            f"{utilization_pct}%",
            "pie-chart",
            color="purple",
            progress=utilization_pct,
        ),
        class_name="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5",
    )


def home_content() -> rx.Component:
    """
    Home content page
    """

    def str_date_now() -> str:
        """Formats the current date as a string like "September 21st, 2024"""
        time_now: datetime = datetime.now()

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
                    class_name="font-['Inter'] font-extrabold text-2xl text-gray-900 dark:text-gray-100 mb-2",
                ),
                date_picker(),
                class_name="flex justify-between items-center w-full",
            ),
            rx.el.p(
                f"Today is {str_date_now()}",
                class_name="text-sm text-gray-600 dark:text-gray-400 mb-6",
            ),
            class_name="mb-6 animate-in fade-in slide-in-from-bottom-4 duration-700",
        ),
        quick_actions_panel(
            open_add_expense_modal=HomeState.open_add_expense_modal,
            open_add_budget_modal=HomeState.open_add_budget_modal,
            open_add_budget_allocations=HomeState.open_add_budget_allocations,
        ),
        rx.el.div(
            stats_grid(
                total_earnings=IncomeState.total_earnings,
                total_expenses=ExpenseState.total_expenses,
                remaining_earnings=(
                    IncomeState.total_earnings - ExpenseState.total_expenses
                ),
                utilization_pct=rx.cond(
                    IncomeState.total_earnings == 0,
                    0.0,
                    round(
                        ExpenseState.total_expenses / IncomeState.total_earnings * 100,
                        1,
                    ),
                ),
            ),
            class_name="mb-5 animate-in fade-in slide-in-from-bottom-6 duration-700 delay-100",
        ),
        rx.el.div(
            rx.el.div(
                budget_chart(display_data=HomeState.budget_vs_actual_spend),
                class_name="lg:col-span-2",
            ),
            rx.el.div(
                category_distribution_widget(
                    icon="wallet",
                    card_title="Total Income",
                    total_earnings=IncomeState.total_earnings,
                    earnings_categories=IncomeState.income_distribution_data,
                ),
                class_name="lg:col-span-1",
            ),
            class_name="grid grid-cols-1 lg:grid-cols-3 gap-5 mb-5 animate-in fade-in slide-in-from-bottom-8 duration-700 delay-200",
        ),
        rx.el.div(
            rx.el.div(
                budget_health_widget(
                    health_stats=HomeState.budget_health_stats,
                    total_expenses=ExpenseState.total_expenses,
                ),
                class_name="lg:col-span-4",
            ),
            rx.el.div(
                activity_feed(
                    title="Recent Activity", transaction_list=HomeState.recent_activity
                ),
                class_name="lg:col-span-3  max-h-[500px] w-full",
            ),
            class_name="grid grid-cols-1 lg:grid-cols-7 gap-5 mb-5 animate-in fade-in slide-in-from-bottom-8 duration-700 delay-200",
        ),
        class_name="max-w-7xl mx-auto relative z-10",
    )
