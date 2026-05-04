""""""

import reflex as rx

from lemonade_stand.ui.states.budget_state import BudgetState


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
                rx.el.p(title, class_name="text-sm font-medium text-gray-500 mb-1"),
                rx.el.h3(
                    value, class_name="text-2xl font-bold text-gray-900 tracking-tight"
                ),
                class_name="flex flex-col",
            ),
            rx.el.div(
                rx.icon(icon, size=24, class_name=f"text-{color}-600"),
                class_name=f"p-3 rounded-xl bg-{color}-50 group-hover:scale-110 transition-transform duration-300 shadow-sm",
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
                    class_name="w-full h-2 bg-gray-100 rounded-full overflow-hidden",
                ),
                rx.el.p(
                    f"{progress}% utilized",
                    class_name=f"text-xs font-medium text-{color}-600 mt-2",
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
                                trend_up, "text-emerald-600", "text-rose-600"
                            ),
                        ),
                        class_name=rx.cond(
                            trend_up,
                            "bg-emerald-100 p-1 rounded-full",
                            "bg-rose-100 p-1 rounded-full",
                        ),
                    ),
                    rx.el.span(trend, class_name="text-xs font-medium text-gray-600"),
                    class_name="flex items-center gap-2",
                ),
                rx.el.div(),
            ),
        ),
        class_name="group bg-white/70 backdrop-blur-xl p-6 rounded-2xl border border-white/50 shadow-[0_8px_30px_rgb(0,0,0,0.04)] hover:shadow-[0_8px_30px_rgb(0,0,0,0.08)] transition-all duration-300 hover:-translate-y-1",
    )


def stats_grid() -> rx.Component:
    """"""

    return rx.el.div(
        stat_card(
            "Total Budget",
            f"${BudgetState.total_budget:,.0f}",
            "wallet",
            trend="+12% from last Q",
            color="blue",
            trend_up=True,
        ),
        stat_card(
            "Total Spent",
            f"${BudgetState.total_spent:,.0f}",
            "credit-card",
            trend="+5% vs target",
            color="indigo",
            trend_up=False,
        ),
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.p(
                        "Remaining", class_name="text-sm font-medium text-gray-500 mb-1"
                    ),
                    rx.el.h3(
                        f"${BudgetState.remaining_budget:,.0f}",
                        class_name=f"text-2xl font-bold {BudgetState.budget_health_color}",
                    ),
                    class_name="flex flex-col",
                ),
                rx.el.div(
                    rx.icon(
                        "piggy-bank",
                        size=24,
                        class_name=BudgetState.budget_health_color,
                    ),
                    class_name=f"p-3 rounded-xl {BudgetState.budget_health_bg}",
                ),
                class_name="flex justify-between items-start mb-4",
            ),
            rx.el.div(
                rx.el.span(
                    "Calculated from active budgets", class_name="text-xs text-gray-400"
                ),
                class_name="mt-auto",
            ),
            class_name="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm hover:shadow-md transition-shadow flex flex-col justify-between",
        ),
        stat_card(
            "Utilization",
            f"{BudgetState.utilization_percentage}%",
            "pie-chart",
            color="purple",
            progress=BudgetState.utilization_percentage,
        ),
        class_name="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6",
    )
