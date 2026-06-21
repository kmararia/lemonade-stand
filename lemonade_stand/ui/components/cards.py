""""""

from decimal import Decimal

import reflex as rx

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
                    class_name=f"text-{transaction.health_color}-600 dark:text-{transaction.health_color}-400 shrink-0",
                ),
                rx.el.div(
                    rx.el.span(
                        transaction.description,
                        class_name="text-sm font-semibold text-gray-900 dark:text-gray-100 w-full block truncate",
                    ),
                    rx.el.span(
                        transaction.date,
                        class_name="text-xs font-medium text-gray-500 dark:text-gray-400 mt-0.5",
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
                    text-{transaction.health_color}-800 dark:text-{transaction.health_color}-400
                    bg-{transaction.health_color}-100 dark:bg-{transaction.health_color}-900/30
                """,
            ),
            class_name="""
                flex justify-between items-center p-3 rounded-lg
                bg-white/70 dark:bg-gray-800/50 backdrop-blur-xl border border-white/50 dark:border-gray-700/50
                transition-all duration-200 group cursor-default
                shrink-0 ml-4
            """,
        )

    return rx.el.div(
        rx.el.div(
            rx.el.h3(
                title,
                class_name="px-2 text-lg font-bold text-gray-900 dark:text-gray-100",
            ),
            rx.el.select(
                rx.el.option("All", value="All"),
                rx.el.option("Income", value="Income"),
                rx.el.option("Savings", value="Savings"),
                rx.el.option("Expenses", value="Expenses"),
                value=ActivityState.activity_filter,
                on_change=ActivityState.set_activity_filter,
                class_name="""
                    text-xs font-medium text-gray-600 dark:text-gray-400
                    bg-gray-50 dark:bg-gray-800 border-none rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700
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
            bg-white/70 dark:bg-gray-800/50 backdrop-blur-xl rounded-2xl border border-white/50 dark:border-gray-700/50
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
                        class_name=f"""
                            text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full w-20 text-center
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
                        }
                        """,
                    ),
                    class_name="flex items-center",
                ),
                class_name="flex items-center",
            ),
            class_name="py-3 px-2 border-b border-gray-50 dark:border-gray-700/50 last:border-0 hover:bg-white/50 dark:hover:bg-gray-700/30 transition-colors rounded-lg",
        )

    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.h3(
                    "Budget Health Overview",
                    class_name="text-lg font-bold text-gray-900 dark:text-gray-100",
                ),
                rx.el.span(
                    f"$ {total_expenses:,.0f}",
                    class_name="text-3xl font-bold text-gray-900 dark:text-gray-100 tracking-tight",
                ),
                class_name="flex flex-col justify-between gap-5 mb-5 animate-in fade-in slide-in-from-bottom-4 duration-700",
            ),
            rx.el.a(
                "Manage",
                href="/budgets",
                class_name="text-sm font-medium text-indigo-600 dark:text-cyan-400 hover:text-indigo-800 transition-colors",
            ),
            class_name="flex items-center justify-between mb-4",
        ),
        rx.el.div(
            rx.foreach(health_stats, budget_health_row),
            class_name="flex flex-col max-h-[300px] overflow-y-auto custom-scrollbar pr-2",
        ),
        class_name="bg-white/70 dark:bg-gray-800/50 backdrop-blur-xl p-7 rounded-2xl border border-white/50 dark:border-gray-700/50 shadow-[0_8px_30px_rgb(0,0,0,0.04)] h-full",
    )


def income_distribution_card(
    earnings_categories: rx.Var[list[dict]],
    total_earnings: rx.Var[int | float | Decimal],
) -> rx.Component:
    """"""

    return rx.el.div(
        # Header Section
        rx.el.div(
            rx.el.div(
                rx.icon(
                    "wallet",
                    size=24,
                    class_name="text-blue-600 dark:text-blue-400/60 transition-colors",
                ),
                rx.el.h3(
                    "Total Income",
                    class_name="text-lg font-bold text-gray-900 dark:text-gray-100",
                ),
                class_name="flex justify-left gap-4",
            ),
            rx.el.button(
                "All accounts",
                rx.icon("chevron-down", size=14, class_name="ml-1"),
                class_name="flex items-center text-sm font-medium text-indigo-600 dark:text-cyan-400 hover:text-indigo-800 transition-colors",
            ),
            class_name="flex justify-between items-center mb-8",
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
                height=220,
            ),
            rx.el.div(
                rx.el.span(
                    f"$ {total_earnings:,.0f}",
                    class_name="pb-10 text-3xl font-bold text-gray-900 dark:text-gray-100 tracking-tight",
                ),
                class_name="absolute inset-0 flex items-center justify-center pointer-events-none",
            ),
            class_name="relative h-[300px] pt-6 w-full",
        ),
        # Custom Legend Section
        rx.el.div(
            rx.foreach(
                earnings_categories,
                lambda item: rx.el.div(
                    rx.el.div(
                        class_name="w-2.5 h-2.5 rounded-full mr-2",
                        style={"backgroundColor": item["fill"]},
                    ),
                    rx.el.span(
                        item["name"],
                        class_name="text-xs font-medium text-gray-500 dark:text-gray-400",
                    ),
                    class_name="flex items-center",
                ),
            ),
            class_name="flex justify-center gap-6",
        ),
        class_name="bg-white/70 dark:bg-gray-800/50 backdrop-blur-xl p-6 rounded-2xl border border-white/50 dark:border-gray-700/50 shadow-[0_8px_30px_rgb(0,0,0,0.04)] h-full",
    )


def stat_card(
    title: str,
    value: str,
    icon: str,
    trend: str | None = None,
    color: str = "indigo",
    progress: rx.Var[int | float | Decimal] | None = None,
    trend_up: bool = True,
) -> rx.Component:
    """"""

    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.p(
                    title,
                    class_name="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1",
                ),
                rx.el.h3(
                    value,
                    class_name="text-2xl font-bold text-gray-900 dark:text-gray-100 tracking-tight",
                ),
                class_name="flex flex-col",
            ),
            rx.el.div(
                rx.icon(
                    icon,
                    size=24,
                    class_name=f"text-{color}-600 dark:text-{color}-400/60 transition-colors",
                ),
                class_name=f"p-3 rounded-xl bg-{color}-50 dark:bg-{color}-900/30 group-hover:scale-110 transition-transform duration-300 shadow-sm",
            ),
            class_name="flex justify-between items-start mb-4",
        ),
        rx.cond(
            progress is not None,
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        class_name=f"h-2 rounded-full bg-gradient-to-r from-{color}-500 to-{color}-400 transition-all duration-1000 ease-out",
                        style={"width": f"{progress}%"},
                    ),
                    class_name="w-full h-2 bg-gray-100 dark:bg-gray-700 rounded-full overflow-hidden",
                ),
                rx.el.p(
                    f"{progress}% utilized",
                    class_name=f"text-xs font-medium text-{color}-600 dark:text-{color}-400 mt-2",
                ),
                class_name="w-full",
            ),
            rx.cond(
                trend is not None,
                rx.el.div(
                    rx.el.div(
                        rx.icon(
                            rx.cond(trend_up, "trending-up", "trending-down"),
                            size=14,
                            class_name=rx.cond(
                                trend_up,
                                "text-emerald-600 dark:text-emerald-400",
                                "text-rose-600 dark:text-rose-400",
                            ),
                        ),
                        class_name=rx.cond(
                            trend_up,
                            "bg-emerald-100 dark:bg-emerald-900/30 p-1 rounded-full",
                            "bg-rose-100 dark:bg-rose-900/30 p-1 rounded-full",
                        ),
                    ),
                    rx.el.span(
                        trend,
                        class_name="text-xs font-medium text-gray-600 dark:text-gray-400",
                    ),
                    class_name="flex items-center gap-2",
                ),
                rx.el.div(),
            ),
        ),
        class_name="group bg-white/70 dark:bg-gray-800/50 backdrop-blur-xl p-6 pl-6 rounded-2xl border border-white/50 dark:border-gray-700/50 shadow-[0_8px_30px_rgb(0,0,0,0.04)] hover:shadow-[0_8px_30px_rgb(0,0,0,0.08)] transition-all duration-300 hover:-translate-y-1",
    )


def stats_grid(
    total_earnings: rx.Var[int | float | Decimal],
    total_expenses: rx.Var[int | float | Decimal],
    remaining_earnings: rx.Var[int | float | Decimal],
    utilization_pct: rx.Var[int | float | Decimal],
) -> rx.Component:
    """"""

    return rx.el.div(
        stat_card(
            "Total Earnings",
            f"${total_earnings:,.0f}",
            "wallet",
            trend="+12% from last Q",
            color="blue",
            trend_up=True,
        ),
        stat_card(
            "Total Spent",
            f"${total_expenses:,.0f}",
            "credit-card",
            trend="+5% vs target",
            color="indigo",
            trend_up=False,
        ),
        stat_card(
            "Remaining Earnings",
            f"${remaining_earnings:,.0f}",
            "piggy-bank",
            color="indigo",
            progress=utilization_pct,
        ),
        stat_card(
            "Utilization",
            f"{utilization_pct}%",
            "pie-chart",
            color="purple",
            progress=utilization_pct,
        ),
        class_name="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5",
    )
