""""""

import typing
from decimal import Decimal

import reflex as rx

from lemonade_stand.ui.states.data_state import TopCategory
from lemonade_stand.ui.states.home_state import BudgetHealthStats
from lemonade_stand.ui.states.home_state import TransactionActivity
from lemonade_stand.ui.states.ui_state import ActivityState


def activity_feed(
    title: str,
    transaction_list: rx.Var[list[TransactionActivity]],
) -> rx.Component:
    """"""

    def activity_row(transaction: TransactionActivity) -> rx.Component:
        """"""

        return rx.el.div(
            rx.el.div(
                rx.icon(
                    transaction.payment_type,
                    size=18,
                    class_name=f"""
                        shrink-0
                        {
                        rx.cond(
                            transaction.amount < 0,
                            "text-[var(--warning-text)]",
                            "text-[var(--healthy-text)]",
                        )
                    }
                    """,
                ),
                rx.el.div(
                    rx.el.span(
                        transaction.description,
                        class_name="text-sm font-semibold text-[var(--text-main)] w-full block truncate",
                    ),
                    rx.el.span(
                        transaction.date,
                        class_name="text-xs font-medium text-[var(--text-muted)] mt-0.5",
                    ),
                    class_name="flex flex-col justify-center flex-1 min-w-0 pr-5",
                ),
                class_name="flex items-center gap-4 flex-1 min-w-0",
            ),
            rx.el.span(
                rx.cond(
                    transaction.amount < 0,
                    f"-${abs(transaction.amount):,.2f}",
                    f"+${transaction.amount:,.2f}",
                ),
                class_name=f"""
                    text-xs font-bold uppercase tracking-wider px-2 py-0.5 rounded-full w-22 text-center
                    {
                    rx.cond(
                        transaction.amount < 0,
                        "bg-[var(--warning-bg)] text-[var(--warning-text)]",
                        "bg-[var(--healthy-bg)] text-[var(--healthy-text)]",
                    )
                }
                """,
            ),
            class_name="""
                flex justify-between items-center p-3 rounded-lg
                bg-[var(--bg-subtle)] backdrop-blur-xl border border-[var(--border-subtle)]
                transition-all duration-200 group cursor-default
                shrink-0 ml-4
            """,
        )

    return rx.el.div(
        rx.el.div(
            rx.el.h3(
                title,
                class_name="px-2 text-lg font-bold text-[var(--text-main)]",
            ),
            rx.el.select(
                rx.el.option("All", value="All"),
                rx.el.option("Income", value="Income"),
                rx.el.option("Savings", value="Savings"),
                rx.el.option("Expenses", value="Expenses"),
                value=ActivityState.activity_filter,
                on_change=ActivityState.set_activity_filter,
                class_name="""
                    text-xs font-medium text-[var(--text-muted)]
                    bg-[var(--bg-subtle)] border-none rounded-lg hover:bg-[var(--bg-card)]
                    focus:ring-1 focus:ring-indigo-500 py-1 pl-2 pr-8 cursor-pointer transition-colors
                """,
            ),
            class_name="flex items-center justify-between mb-6 shrink-0",
        ),
        rx.el.div(
            rx.foreach(transaction_list, activity_row),
            class_name="flex-1 flex flex-col overflow-y-auto custom-scrollbar pr-2 gap-2",
        ),
        class_name="""
            py-6 px-4 flex flex-col
            bg-[var(--bg-card)] backdrop-blur-xl rounded-2xl border border-[var(--border-main)]
            shadow-[0_8px_30px_rgb(0,0,0,0.04)] h-full min-h-0 overflow-hidden
        """,
    )


def budget_health_widget(
    health_stats: rx.Var[list[BudgetHealthStats]],
    total_expenses: rx.Var[int | float | Decimal],
) -> rx.Component:
    """"""

    def budget_health_row(budget: BudgetHealthStats) -> rx.Component:
        """"""
        return rx.el.div(
            rx.el.div(
                rx.el.span(
                    budget.category,
                    class_name="text-sm font-semibold text-[var(--text-main)] w-32 truncate",
                ),
                rx.el.div(
                    rx.el.div(
                        class_name=f"""
                            h-2 rounded-full
                            {
                            rx.cond(
                                budget.utilization > 90,
                                "bg-[var(--critical-text)]",
                                rx.cond(
                                    budget.utilization > 75,
                                    "bg-[var(--warning-text)]",
                                    "bg-[var(--healthy-text)]",
                                ),
                            )
                        }
                        """,
                        style={"width": f"{budget.utilization}%"},
                    ),
                    class_name="flex-1 h-2 bg-[var(--bg-subtle)] rounded-full overflow-hidden mx-3",
                ),
                rx.el.div(
                    rx.el.span(
                        f"{budget.utilization}%",
                        class_name="text-xs font-bold text-[var(--text-muted)] w-12 text-right mr-3",
                    ),
                    rx.el.span(
                        rx.cond(
                            budget.utilization > 90,
                            "Critical",
                            rx.cond(budget.utilization > 75, "Warning", "Healthy"),
                        ),
                        class_name=f"""
                            text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full w-20 text-center
                            {
                            rx.cond(
                                budget.utilization > 90,
                                "bg-[var(--critical-bg)] text-[var(--critical-text)]",
                                rx.cond(
                                    budget.utilization > 75,
                                    "bg-[var(--warning-bg)] text-[var(--warning-text)]",
                                    "bg-[var(--healthy-bg)] text-[var(--healthy-text)]",
                                ),
                            )
                        }
                        """,
                    ),
                    class_name="flex items-center",
                ),
                class_name="flex items-center",
            ),
            class_name="py-3 px-2 border-b border-[var(--border-subtle)] last:border-0 hover:bg-[var(--bg-subtle)] transition-colors rounded-lg",
        )

    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.h3(
                    "Budget Health Overview",
                    class_name="text-lg font-bold text-[var(--text-main)]",
                ),
                rx.el.span(
                    f"$ {total_expenses:,.0f}",
                    class_name="text-3xl font-bold text-[var(--text-main)] tracking-tight",
                ),
                class_name="flex flex-col justify-between gap-5 mb-5 animate-in fade-in slide-in-from-bottom-4 duration-700",
            ),
            rx.el.a(
                "Manage",
                href="/budgets",
                class_name="text-sm font-medium text-[var(--selected-color)] hover:text-[var(--healthy-text)] transition-colors",
            ),
            class_name="flex items-center justify-between mb-4",
        ),
        rx.el.div(
            rx.foreach(health_stats, budget_health_row),
            class_name="flex flex-col max-h-[300px] overflow-y-auto custom-scrollbar pr-2",
        ),
        class_name="bg-[var(--bg-card)] backdrop-blur-xl p-7 rounded-2xl border border-[var(--border-main)] shadow-[0_8px_30px_rgb(0,0,0,0.04)] h-full",
    )


def category_distribution_widget(
    icon: str,
    card_title: str,
    total_earnings: rx.Var[int | float | Decimal],
    earnings_categories: rx.Var[list[dict]],
) -> rx.Component:
    """"""

    return rx.el.div(
        # Header Section
        rx.el.div(
            rx.el.div(
                rx.icon(
                    icon,
                    size=24,
                    class_name="text-[var(--selected-color)] transition-colors",
                ),
                rx.el.h3(
                    card_title,
                    class_name="text-lg font-bold text-[var(--text-main)]",
                ),
                class_name="flex justify-left gap-4",
            ),
            rx.el.button(
                "All accounts",
                rx.icon("chevron-down", size=14, class_name="ml-1"),
                class_name="""
                    flex items-center
                    text-xs font-medium text-[var(--text-muted)]
                    bg-[var(--bg-subtle)] border-none rounded-lg hover:bg-[var(--bg-card)]
                    focus:ring-1 focus:ring-indigo-500 py-1 px-2 cursor-pointer transition-colors
                """,
            ),
            class_name="flex justify-between items-center mb-10",
        ),
        # Chart Section
        rx.el.div(
            # The Recharts Doughnut
            rx.recharts.responsive_container(
                rx.recharts.pie_chart(
                    rx.recharts.pie(
                        data=earnings_categories,
                        data_key="amount",
                        name_key="name",
                        cx="50%",
                        cy="50%",
                        inner_radius="90%",
                        outer_radius="100%",
                        padding_angle=6,
                        corner_radius=8,
                        stroke="none",
                    ),
                ),
                width="100%",
                height="100%",
            ),
            rx.el.div(
                rx.el.span(
                    f"$ {total_earnings:,.0f}",
                    class_name="text-3xl font-bold text-[var(--text-main)] tracking-tight",
                ),
                class_name="absolute inset-0 flex items-center justify-center pointer-events-none",
            ),
            class_name="relative flex-1 min-h-0 w-full mb-10",
        ),
        # Custom Legend Section
        rx.el.div(
            rx.foreach(
                earnings_categories,
                lambda item: rx.el.div(
                    rx.el.div(
                        class_name="w-2.5 h-2.5 rounded-full mr-2 shrink-0",
                        style={"backgroundColor": item["fill"]},
                    ),
                    rx.el.span(
                        item["name"],
                        class_name="text-xs font-medium text-[var(--text-muted)] truncate",
                    ),
                    class_name="flex items-center mx-4",
                ),
            ),
            class_name="""
                grid grid-cols-2 sm:grid-cols-3 gap-x-6 gap-y-3 mx-auto w-fit
                max-h-32 overflow-y-auto pr-2 custom-scrollbar
            """,
        ),
        class_name="flex flex-col bg-[var(--bg-card)] backdrop-blur-xl p-6 rounded-2xl border border-[var(--border-main)] shadow-sm h-full overflow-hidden",
    )


def top_category_widget(
    card_title: str, amount_title: str, top_category_list: rx.Var[list[typing.Any]]
) -> rx.Component:
    """"""

    def top_category_row(category: TopCategory) -> rx.Component:
        return rx.el.div(
            rx.el.div(
                rx.match(
                    category.index,
                    (1, rx.el.span("🥇", class_name="text-lg w-8 text-center")),
                    (2, rx.el.span("🥈", class_name="text-lg w-8 text-center")),
                    (3, rx.el.span("🥉", class_name="text-lg w-8 text-center")),
                    rx.el.span(
                        f"#{category.index}",
                        class_name="text-xs font-bold text-gray-400 w-8 text-center",
                    ),
                ),
                rx.image(
                    src=f"https://api.dicebear.com/10.x/shapes/svg?seed={category.index}",
                    class_name="w-10 h-10 rounded-full bg-gray-50 border-2 border-white shadow-sm mr-3 ml-1",
                ),
                rx.el.p(
                    category.name,
                    class_name="text-sm font-semibold text-[var(--text-main)]",
                ),
                class_name="flex items-center flex-1",
            ),
            rx.el.div(
                rx.el.p(
                    f"${category.amount:,.0f}",
                    class_name="text-sm font-bold text-[var(--text-main)]",
                ),
                rx.el.p(
                    amount_title,
                    class_name="text-[10px] text-gray-400 font-medium text-right",
                ),
                class_name="text-right",
            ),
            class_name="flex items-center justify-between py-3 px-2 rounded-xl hover:bg-[var(--bg-subtle)] transition-colors border-b border-[var(--border-subtle)] last:border-0",
        )

    return rx.el.div(
        rx.el.h3(
            card_title,
            class_name="text-lg font-bold text-[var(--text-main)] mb-4 pb-2",
        ),
        rx.el.div(
            rx.foreach(top_category_list, top_category_row),
            class_name="flex flex-col",
        ),
        class_name="bg-[var(--bg-card)] backdrop-blur-xl p-6 rounded-2xl border border-[var(--border-main)] shadow-sm h-full",
    )
