""""""

import reflex as rx

from lemonade_stand.ui.states.goals_state import Goal
from lemonade_stand.ui.states.goals_state import GoalsState


def goal_stat_item(label: str, value: int, color: str, icon: str) -> rx.Component:
    """"""
    return rx.el.div(
        rx.el.div(
            rx.icon(
                icon, size=16, class_name=f"text-{color}-600 dark:text-{color}-400 mb-1"
            ),
            rx.el.span(
                value, class_name="text-xl font-bold text-gray-900 dark:text-gray-100"
            ),
            class_name=f"flex flex-col items-center justify-center p-3 rounded-xl bg-{color}-50 dark:bg-{color}-900/20 w-full",
        ),
        rx.el.span(
            label,
            class_name="text-xs font-medium text-gray-500 dark:text-gray-400 mt-1 text-center block",
        ),
        class_name="flex flex-col items-center flex-1",
    )


def goal_dashboard_item(goal: Goal) -> rx.Component:
    """"""

    progress = rx.cond(
        goal["target_amount"] > 0,
        goal["current_amount"] / goal["target_amount"] * 100,
        0,
    )
    """"""

    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.span(
                    goal["name"],
                    class_name="text-sm font-semibold text-gray-900 dark:text-gray-100 truncate",
                ),
                rx.el.span(
                    goal["deadline"],
                    class_name="text-xs text-gray-400 ml-2 whitespace-nowrap",
                ),
                class_name="flex justify-between items-center mb-1",
            ),
            rx.el.div(
                rx.el.div(
                    class_name=rx.cond(
                        goal["status"] == "Completed",
                        "h-1.5 rounded-full bg-emerald-500",
                        rx.cond(
                            goal["status"] == "At Risk",
                            "h-1.5 rounded-full bg-orange-500",
                            "h-1.5 rounded-full bg-indigo-500 dark:bg-cyan-500",
                        ),
                    ),
                    style={"width": f"{progress}%"},
                ),
                class_name="w-full h-1.5 bg-gray-100 dark:bg-gray-700 rounded-full overflow-hidden",
            ),
            rx.el.div(
                rx.el.span(
                    f"{progress:.0f}%",
                    class_name="text-xs font-medium text-gray-500 dark:text-gray-400",
                ),
                rx.el.span(
                    goal["status"],
                    class_name=rx.cond(
                        goal["status"] == "Completed",
                        "text-xs font-medium text-emerald-600 dark:text-emerald-400",
                        rx.cond(
                            goal["status"] == "At Risk",
                            "text-xs font-medium text-orange-600 dark:text-orange-400",
                            "text-xs font-medium text-indigo-600 dark:text-cyan-400",
                        ),
                    ),
                ),
                class_name="flex justify-between items-center mt-1",
            ),
            class_name="w-full",
        ),
        class_name="py-3 border-b border-gray-50 dark:border-gray-700/50 last:border-0",
    )


def goals_widget() -> rx.Component:
    """"""

    return rx.el.div(
        rx.el.div(
            rx.el.h3(
                "Goals Snapshot",
                class_name="text-lg font-bold text-gray-900 dark:text-gray-100",
            ),
            rx.el.a(
                "View All",
                href="/goals",
                class_name="text-sm font-medium text-indigo-600 dark:text-cyan-400 hover:text-indigo-800 transition-colors",
            ),
            class_name="flex items-center justify-between mb-4",
        ),
        rx.el.div(
            goal_stat_item("Active", GoalsState.total_goals_count, "blue", "target"),
            goal_stat_item(
                "Completed",
                GoalsState.completed_goals_count,
                "emerald",
                "circle_check_big",
            ),
            goal_stat_item(
                "At Risk", GoalsState.at_risk_goals_count, "orange", "trending_down"
            ),
            class_name="flex gap-3 mb-6",
        ),
        rx.el.div(
            rx.foreach(GoalsState.dashboard_goals, goal_dashboard_item),
            class_name="flex flex-col",
        ),
        class_name="bg-white/70 dark:bg-gray-800/50 backdrop-blur-xl p-6 rounded-2xl border border-white/50 dark:border-gray-700/50 shadow-[0_8px_30px_rgb(0,0,0,0.04)] h-full",
    )
