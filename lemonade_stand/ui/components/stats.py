""""""

import reflex as rx


def stat_card(
    title: str,
    value: str,
    icon: str,
    trend: str = None,
    color: str = "indigo",
    progress: float = None,
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
        class_name="group bg-white/70 dark:bg-gray-800/50 backdrop-blur-xl p-6 rounded-2xl border border-white/50 dark:border-gray-700/50 shadow-[0_8px_30px_rgb(0,0,0,0.04)] hover:shadow-[0_8px_30px_rgb(0,0,0,0.08)] transition-all duration-300 hover:-translate-y-1",
    )


def stats_grid(
    total_budget: float,
    total_spent: float,
    remaining_budget: float,
    utilization_pct: float,
) -> rx.Component:
    """"""

    return rx.el.div(
        stat_card(
            "Total Budget",
            f"${total_budget:,.0f}",
            "wallet",
            trend="+12% from last Q",
            color="blue",
            trend_up=True,
        ),
        stat_card(
            "Total Spent",
            f"${total_spent:,.0f}",
            "credit-card",
            trend="+5% vs target",
            color="indigo",
            trend_up=False,
        ),
        stat_card(
            "Remaining Budget",
            f"${remaining_budget:,.0f}",
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
