""""""

from datetime import datetime
from decimal import Decimal

import reflex as rx

from lemonade_stand.ui.components.charts import budget_chart
from lemonade_stand.ui.components.date_picker import date_picker
from lemonade_stand.ui.components.layout import page_layout
from lemonade_stand.ui.components.small_cards import summary_stats_card
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
                    class_name=f"text-{color}-600 dark:text-{color}-400 mb-2",
                ),
                rx.el.span(
                    label,
                    class_name="text-xs font-semibold text-[var(--text-main)] group-hover:text-[var(--text-accent)] transition-colors",
                ),
                class_name="""
                    flex flex-col items-center justify-center p-4
                    bg-[var(--bg-card)] rounded-xl border border-[var(--border-main)]
                    shadow-sm hover:shadow-md transition-all duration-300 hover:-translate-y-1
                    w-full h-full group
                """,
            ),
            on_click=on_click,
            class_name="w-full pt-4",
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
    remaining_earnings: rx.Var[int | float | Decimal],
    utilization_pct: rx.Var[int | float | Decimal],
) -> rx.Component:
    """"""

    return rx.el.div(
        summary_stats_card(
            "Total Earnings",
            f"${IncomeState.total_earnings:,.0f}",
            (
                "+12% from last Q",  # TODO: update with real values
                rx.cond(
                    IncomeState.percentage_of_target_earned >= 20,
                    "trending-up",
                    "trending-down",
                ),
                rx.cond(
                    IncomeState.percentage_of_target_earned >= 20,
                    "emerald",
                    "red",
                ),
            ),
            icon="wallet",
            icon_color="emerald",
        ),
        summary_stats_card(
            "Total Spent",
            f"${ExpenseState.total_expenses:,.2f}",
            (
                f"{ExpenseState.remaining_budget_percentage:.0f}% of total",
                rx.cond(
                    ExpenseState.percentage_of_income_spent < 100,
                    "trending-up",
                    "trending-down",
                ),
                rx.cond(
                    ExpenseState.percentage_of_income_spent < 100,
                    "emerald",
                    "red",
                ),
            ),
            icon="dollar-sign",
            icon_color="orange",
        ),
        summary_stats_card(
            "Remaining Earnings",
            f"${remaining_earnings:,.0f}",
            (
                f"{utilization_pct:.0f}% utilized",
                rx.cond(
                    remaining_earnings.to(float) > 0, "trending-up", "trending-down"
                ),
                rx.cond(remaining_earnings.to(float) > 0, "emerald", "red"),
            ),
            icon="piggy-bank",
            icon_color="blue",
            progress=utilization_pct,
        ),
        summary_stats_card(
            "Utilization",
            f"{utilization_pct:.0f}%",
            (
                f"{utilization_pct:.0f}% utilized",
                rx.cond(utilization_pct.to(float) > 80, "trending-up", "trending-down"),
                rx.cond(utilization_pct.to(float) > 80, "red", "emerald"),
            ),
            icon="pie-chart",
            icon_color="purple",
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

    return page_layout(
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.h2(
                        "Overview",
                        class_name="font-['Inter'] font-extrabold text-2xl text-[var(--text-main)] mb-2",
                    ),
                    date_picker(),
                    class_name="flex justify-between items-center w-full",
                ),
                rx.el.p(
                    f"Today is {str_date_now()}",
                    class_name="text-sm text-[var(--text-muted)]",
                ),
                class_name="w-full mb-6 animate-in fade-in slide-in-from-bottom-4 duration-700",
            ),
            quick_actions_panel(
                open_add_expense_modal=HomeState.open_add_expense_modal,
                open_add_budget_modal=HomeState.open_add_budget_modal,
                open_add_budget_allocations=HomeState.open_add_budget_allocations,
            ),
            rx.el.div(
                stats_grid(
                    remaining_earnings=(
                        IncomeState.total_earnings - ExpenseState.total_expenses
                    ),
                    utilization_pct=rx.cond(
                        IncomeState.total_earnings == 0,
                        0.0,
                        round(
                            ExpenseState.total_expenses
                            / IncomeState.total_earnings
                            * 100,
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
                class_name="grid grid-cols-1 lg:grid-cols-3 gap-5 mb-5 animate-in fade-in slide-in-from-bottom-8 duration-700",
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
                        title="Recent Activity",
                        transaction_list=HomeState.recent_activity,
                    ),
                    class_name="lg:col-span-3  max-h-[500px] w-full",
                ),
                class_name="grid grid-cols-1 lg:grid-cols-7 gap-5 mb-5 animate-in fade-in slide-in-from-bottom-8 duration-700",
            ),
            class_name="w-full mx-auto relative z-10",
        )
    )
