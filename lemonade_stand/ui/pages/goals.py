""""""

import reflex as rx

from lemonade_stand.ui.components.empty_state import empty_state
from lemonade_stand.ui.components.header import header
from lemonade_stand.ui.components.sidebar import sidebar
from lemonade_stand.ui.states.goals_state import Goal
from lemonade_stand.ui.states.goals_state import GoalsState


def goal_status_badge(status: str) -> rx.Component:
    """"""

    return rx.match(
        status,
        (
            "Completed",
            rx.el.span(
                "Completed",
                class_name="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-100 text-emerald-800",
            ),
        ),
        (
            "On Track",
            rx.el.span(
                "On Track",
                class_name="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800",
            ),
        ),
        (
            "At Risk",
            rx.el.span(
                "At Risk",
                class_name="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-orange-100 text-orange-800",
            ),
        ),
        rx.el.span(
            status,
            class_name="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800",
        ),
    )


def goal_card(goal: Goal) -> rx.Component:
    """"""
    progress = rx.cond(
        goal["target_amount"] > 0,
        goal["current_amount"] / goal["target_amount"] * 100,
        0,
    )
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.span(
                        goal["category"],
                        class_name="text-xs font-semibold text-indigo-600 dark:text-cyan-400 uppercase tracking-wider mb-1 block",
                    ),
                    rx.el.h3(
                        goal["name"],
                        class_name="text-lg font-bold text-gray-900 dark:text-gray-100 line-clamp-1",
                    ),
                ),
                goal_status_badge(goal["status"]),
                class_name="flex justify-between items-start mb-4",
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.span(
                        "Progress",
                        class_name="text-xs font-medium text-gray-500 dark:text-gray-400",
                    ),
                    rx.el.span(
                        f"{progress:.0f}%", class_name="text-xs font-bold text-gray-700"
                    ),
                    class_name="flex justify-between mb-2",
                ),
                rx.el.div(
                    rx.el.div(
                        class_name=rx.cond(
                            goal["status"] == "Completed",
                            "h-2 rounded-full bg-emerald-500 transition-all duration-1000",
                            rx.cond(
                                goal["status"] == "At Risk",
                                "h-2 rounded-full bg-orange-500 transition-all duration-1000",
                                "h-2 rounded-full bg-blue-500 transition-all duration-1000",
                            ),
                        ),
                        style={"width": f"{progress}%"},
                    ),
                    class_name="w-full h-2 bg-gray-100 rounded-full overflow-hidden mb-4",
                ),
                rx.el.div(
                    rx.el.div(
                        rx.el.p(
                            "Current", class_name="text-xs text-gray-400 font-medium"
                        ),
                        rx.el.p(
                            f"${goal['current_amount']:,.0f}",
                            class_name="text-sm font-bold text-gray-900 dark:text-gray-100",
                        ),
                    ),
                    rx.el.div(
                        rx.el.p(
                            "Target",
                            class_name="text-xs text-gray-400 font-medium text-right",
                        ),
                        rx.el.p(
                            f"${goal['target_amount']:,.0f}",
                            class_name="text-sm font-bold text-gray-900 dark:text-gray-100 text-right",
                        ),
                    ),
                    class_name="flex justify-between items-end",
                ),
                class_name="mb-6",
            ),
            rx.el.div(
                rx.el.div(
                    rx.icon("calendar", size=14, class_name="text-gray-400 mr-2"),
                    rx.el.span(
                        f"Due {goal['deadline']}",
                        class_name="text-xs text-gray-500 dark:text-gray-400",
                    ),
                    class_name="flex items-center",
                ),
                rx.el.div(
                    rx.el.button(
                        rx.icon("pencil", size=14, class_name="text-gray-400"),
                        on_click=lambda: GoalsState.open_edit_modal(goal),
                        class_name="p-1.5 hover:bg-gray-100 rounded-lg transition-colors mr-1",
                    ),
                    rx.el.button(
                        rx.icon("trash-2", size=14, class_name="text-gray-400"),
                        on_click=lambda: GoalsState.delete_goal(goal["id"]),
                        class_name="p-1.5 hover:bg-red-50 hover:text-red-500 rounded-lg transition-colors",
                    ),
                    class_name="flex items-center",
                ),
                class_name="flex justify-between items-center pt-4 border-t border-gray-100",
            ),
        ),
        class_name="bg-white/70 dark:bg-gray-800/50 backdrop-blur-xl p-6 rounded-2xl border border-white/50 dark:border-gray-700/50 shadow-[0_8px_30px_rgb(0,0,0,0.04)] hover:shadow-[0_8px_30px_rgb(0,0,0,0.08)] transition-all duration-300 hover:-translate-y-1",
    )


def goal_modal() -> rx.Component:
    """"""

    return rx.cond(
        GoalsState.is_modal_open,
        rx.el.div(
            rx.el.div(
                class_name="fixed inset-0 bg-black/50 backdrop-blur-sm transition-opacity",
                on_click=GoalsState.close_modal,
            ),
            rx.el.div(
                rx.el.h3(
                    rx.cond(
                        GoalsState.current_goal["id"], "Edit Goal", "New Savings Goal"
                    ),
                    class_name="text-lg font-bold text-gray-900 dark:text-gray-100 mb-4",
                ),
                rx.el.div(
                    rx.el.div(
                        rx.el.label(
                            "Goal Name",
                            class_name="block text-sm font-medium text-gray-700 mb-1",
                        ),
                        rx.el.input(
                            default_value=GoalsState.current_goal["name"],
                            on_change=lambda v: GoalsState.update_current_goal(
                                "name", v
                            ),
                            class_name="w-full rounded-lg border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 px-4 py-2 border",
                            placeholder="e.g. Emergency Fund",
                        ),
                        class_name="mb-4",
                    ),
                    rx.el.div(
                        rx.el.div(
                            rx.el.label(
                                "Target Amount",
                                class_name="block text-sm font-medium text-gray-700 mb-1",
                            ),
                            rx.el.input(
                                type="number",
                                default_value=GoalsState.current_goal["target_amount"],
                                on_change=lambda v: GoalsState.update_current_goal(
                                    "target_amount", v
                                ),
                                class_name="w-full rounded-lg border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 px-4 py-2 border",
                            ),
                            class_name="col-span-1",
                        ),
                        rx.el.div(
                            rx.el.label(
                                "Current Saved",
                                class_name="block text-sm font-medium text-gray-700 mb-1",
                            ),
                            rx.el.input(
                                type="number",
                                default_value=GoalsState.current_goal["current_amount"],
                                on_change=lambda v: GoalsState.update_current_goal(
                                    "current_amount", v
                                ),
                                class_name="w-full rounded-lg border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 px-4 py-2 border",
                            ),
                            class_name="col-span-1",
                        ),
                        class_name="grid grid-cols-2 gap-4 mb-4",
                    ),
                    rx.el.div(
                        rx.el.div(
                            rx.el.label(
                                "Category",
                                class_name="block text-sm font-medium text-gray-700 mb-1",
                            ),
                            rx.el.select(
                                rx.el.option("General", value="General"),
                                rx.el.option("Savings", value="Savings"),
                                rx.el.option("Equipment", value="Equipment"),
                                rx.el.option("Events", value="Events"),
                                rx.el.option("Technology", value="Technology"),
                                rx.el.option("Expansion", value="Expansion"),
                                value=GoalsState.current_goal["category"],
                                on_change=lambda v: GoalsState.update_current_goal(
                                    "category", v
                                ),
                                class_name="w-full rounded-lg border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 px-4 py-2 border",
                            ),
                            class_name="col-span-1",
                        ),
                        rx.el.div(
                            rx.el.label(
                                "Deadline",
                                class_name="block text-sm font-medium text-gray-700 mb-1",
                            ),
                            rx.el.input(
                                type="date",
                                default_value=GoalsState.current_goal["deadline"],
                                on_change=lambda v: GoalsState.update_current_goal(
                                    "deadline", v
                                ),
                                class_name="w-full rounded-lg border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 px-4 py-2 border",
                            ),
                            class_name="col-span-1",
                        ),
                        class_name="grid grid-cols-2 gap-4 mb-4",
                    ),
                    rx.el.div(
                        rx.el.label(
                            "Status",
                            class_name="block text-sm font-medium text-gray-700 mb-1",
                        ),
                        rx.el.select(
                            rx.el.option("On Track", value="On Track"),
                            rx.el.option("At Risk", value="At Risk"),
                            rx.el.option("Completed", value="Completed"),
                            value=GoalsState.current_goal["status"],
                            on_change=lambda v: GoalsState.update_current_goal(
                                "status", v
                            ),
                            class_name="w-full rounded-lg border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 px-4 py-2 border",
                        ),
                        class_name="mb-4",
                    ),
                    rx.el.div(
                        rx.el.label(
                            "Notes",
                            class_name="block text-sm font-medium text-gray-700 mb-1",
                        ),
                        rx.el.textarea(
                            default_value=GoalsState.current_goal["notes"],
                            on_change=lambda v: GoalsState.update_current_goal(
                                "notes", v
                            ),
                            class_name="w-full rounded-lg border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 px-4 py-2 border",
                            rows="3",
                        ),
                        class_name="mb-6",
                    ),
                    rx.el.div(
                        rx.el.button(
                            "Cancel",
                            on_click=GoalsState.close_modal,
                            class_name="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 mr-3",
                        ),
                        rx.el.button(
                            "Save Goal",
                            on_click=GoalsState.save_goal,
                            class_name="px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700",
                        ),
                        class_name="flex justify-end",
                    ),
                ),
                class_name="relative bg-white rounded-2xl shadow-xl max-w-md w-full p-6 z-50 animate-in fade-in zoom-in duration-200",
            ),
            class_name="fixed inset-0 z-50 flex items-center justify-center p-4",
        ),
        rx.el.div(),
    )


def fab_add_goal() -> rx.Component:
    """"""

    return rx.el.button(
        rx.icon("plus", size=24, class_name="text-white"),
        on_click=GoalsState.open_add_modal,
        class_name="fixed bottom-8 right-8 w-14 h-14 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-full shadow-lg shadow-indigo-300 flex items-center justify-center hover:scale-110 active:scale-95 transition-all duration-300 z-50 animate-bounce-in",
        title="Add New Goal",
    )


def goals_page() -> rx.Component:
    """"""

    return rx.el.div(
        rx.el.div(
            class_name="fixed inset-0 bg-gradient-to-br from-indigo-50/50 via-purple-50/30 to-white -z-10"
        ),
        sidebar(),
        rx.el.div(
            header(),
            rx.el.main(
                rx.el.div(
                    rx.el.div(
                        rx.el.div(
                            rx.el.h2(
                                "Goals & Savings",
                                class_name="text-3xl font-bold text-gray-900 dark:text-gray-100 tracking-tight",
                            ),
                            rx.el.p(
                                "Track your progress towards financial targets.",
                                class_name="text-gray-500 dark:text-gray-400 mt-2 text-lg",
                            ),
                        ),
                        class_name="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-10",
                    ),
                    rx.cond(
                        GoalsState.goals.length() > 0,
                        rx.el.div(
                            rx.foreach(GoalsState.goals, goal_card),
                            class_name="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6 animate-in fade-in slide-in-from-bottom-6 duration-700",
                        ),
                        empty_state(
                            icon="target",
                            title="No goals yet",
                            description="Set financial targets to track your savings progress and achievements.",
                            action_label="Set First Goal",
                            on_click=GoalsState.open_add_modal,
                        ),
                    ),
                    goal_modal(),
                    fab_add_goal(),
                    class_name="max-w-7xl mx-auto relative z-10",
                ),
                class_name="flex-1 p-6 md:p-8 overflow-y-auto scroll-smooth",
            ),
            class_name="flex-1 flex flex-col h-screen overflow-hidden",
        ),
        class_name="flex h-screen bg-gray-50 font-['Inter']",
    )
