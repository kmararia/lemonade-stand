""""""

from decimal import Decimal

import reflex as rx


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
        class_name="bg-white/70 dark:bg-gray-800/50 backdrop-blur-xl p-8 rounded-2xl border border-white/50 dark:border-gray-700/50 shadow-[0_8px_30px_rgb(0,0,0,0.04)] h-full",
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
        class_name="group bg-white/70 dark:bg-gray-800/50 backdrop-blur-xl p-6 pl-8 rounded-2xl border border-white/50 dark:border-gray-700/50 shadow-[0_8px_30px_rgb(0,0,0,0.04)] hover:shadow-[0_8px_30px_rgb(0,0,0,0.08)] transition-all duration-300 hover:-translate-y-1",
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
        class_name="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6",
    )
