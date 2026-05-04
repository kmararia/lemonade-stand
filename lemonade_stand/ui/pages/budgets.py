""""""

import reflex as rx

from lemonade_stand.ui.components.empty_state import empty_state
from lemonade_stand.ui.components.header import header
from lemonade_stand.ui.components.sidebar import sidebar
from lemonade_stand.ui.states.budget_state import BudgetState
from lemonade_stand.ui.states.budget_state import BudgetStats


def budget_modal() -> rx.Component:
    """"""

    return rx.cond(
        BudgetState.is_budget_modal_open,
        rx.el.div(
            rx.el.div(
                class_name="fixed inset-0 bg-black/50 backdrop-blur-sm transition-opacity",
                on_click=BudgetState.close_budget_modal,
            ),
            rx.el.div(
                rx.el.h3(
                    rx.cond(
                        BudgetState.current_budget["id"], "Edit Budget", "New Budget"
                    ),
                    class_name="text-lg font-bold text-gray-900 mb-4",
                ),
                rx.el.div(
                    rx.el.div(
                        rx.el.label(
                            "Budget Name",
                            class_name="block text-sm font-medium text-gray-700 mb-1",
                        ),
                        rx.el.input(
                            on_change=lambda val: BudgetState.update_current_budget(
                                "name", val
                            ),
                            class_name="w-full rounded-lg border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 px-4 py-2 border",
                            placeholder="e.g., Marketing Q1",
                            default_value=BudgetState.current_budget["name"],
                        ),
                        class_name="mb-4",
                    ),
                    rx.el.div(
                        rx.el.label(
                            "Type",
                            class_name="block text-sm font-medium text-gray-700 mb-1",
                        ),
                        rx.el.select(
                            rx.el.option("Department", value="Department"),
                            rx.el.option("Project", value="Project"),
                            rx.el.option("Category", value="Category"),
                            value=BudgetState.current_budget["type"],
                            on_change=lambda val: BudgetState.update_current_budget(
                                "type", val
                            ),
                            class_name="w-full rounded-lg border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 px-4 py-2 border",
                        ),
                        class_name="mb-4",
                    ),
                    rx.el.div(
                        rx.el.div(
                            rx.el.label(
                                "Allocated Amount",
                                class_name="block text-sm font-medium text-gray-700 mb-1",
                            ),
                            rx.el.input(
                                type="number",
                                on_change=lambda val: BudgetState.update_current_budget(
                                    "allocated_amount", val
                                ),
                                class_name="w-full rounded-lg border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 px-4 py-2 border",
                                default_value=BudgetState.current_budget[
                                    "allocated_amount"
                                ],
                            ),
                            class_name="col-span-1",
                        ),
                        rx.el.div(
                            rx.el.label(
                                "Period",
                                class_name="block text-sm font-medium text-gray-700 mb-1",
                            ),
                            rx.el.select(
                                rx.el.option("Annual", value="Annual"),
                                rx.el.option("Q1", value="Q1"),
                                rx.el.option("Q2", value="Q2"),
                                rx.el.option("Q3", value="Q3"),
                                rx.el.option("Q4", value="Q4"),
                                rx.el.option("One-time", value="One-time"),
                                value=BudgetState.current_budget["period"],
                                on_change=lambda val: BudgetState.update_current_budget(
                                    "period", val
                                ),
                                class_name="w-full rounded-lg border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 px-4 py-2 border",
                            ),
                            class_name="col-span-1",
                        ),
                        class_name="grid grid-cols-2 gap-4 mb-6",
                    ),
                    rx.el.div(
                        rx.el.button(
                            "Cancel",
                            on_click=BudgetState.close_budget_modal,
                            class_name="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 mr-3",
                        ),
                        rx.el.button(
                            "Save Budget",
                            on_click=BudgetState.save_budget,
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


def circular_progress(percentage: float, color: str) -> rx.Component:
    """"""

    radius = 20
    circumference = 2 * 3.14159 * radius
    visual_pct = rx.cond(percentage > 100, 100, percentage)
    return rx.el.div(
        rx.el.svg(
            rx.el.circle(
                cx="28",
                cy="28",
                r=str(radius),
                stroke="currentColor",
                stroke_width="4",
                fill="transparent",
                class_name="text-gray-100",
            ),
            rx.el.circle(
                cx="28",
                cy="28",
                r=str(radius),
                stroke="currentColor",
                stroke_width="4",
                fill="transparent",
                stroke_dasharray=f"{circumference}",
                stroke_dashoffset=f"{circumference}px",
                style={
                    "strokeDashoffset": f"calc({circumference}px - ({visual_pct} / 100 * {circumference}px))"
                },
                stroke_linecap="round",
                class_name=f"{color} transition-all duration-1000 ease-out origin-center -rotate-90",
            ),
            view_box="0 0 56 56",
            class_name="w-20 h-20",
        ),
        rx.el.div(
            rx.el.span(
                f"{percentage:.0f}%", class_name="text-xs font-bold text-gray-700"
            ),
            class_name="absolute inset-0 flex items-center justify-center",
        ),
        class_name="relative",
    )


def budget_card(budget: BudgetStats) -> rx.Component:
    """"""

    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.h3(
                            budget["name"],
                            class_name="text-lg font-bold text-gray-900 truncate",
                        ),
                        rx.el.span(
                            budget["type"],
                            class_name="ml-2 px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-gray-100 text-gray-500",
                        ),
                        class_name="flex items-center mb-1",
                    ),
                    rx.el.p(
                        f"${budget['allocated_amount']:,.0f}",
                        class_name="text-2xl font-bold text-indigo-600",
                    ),
                    class_name="flex-1 min-w-0",
                ),
                circular_progress(budget["utilization"], budget["health_color"]),
                class_name="flex justify-between items-start mb-6",
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.p(
                        "Spent",
                        class_name="text-xs text-gray-400 font-medium uppercase tracking-wider mb-1",
                    ),
                    rx.el.p(
                        f"${budget['spent']:,.0f}",
                        class_name="text-sm font-bold text-gray-700",
                    ),
                ),
                rx.el.div(
                    rx.el.p(
                        "Remaining",
                        class_name="text-xs text-gray-400 font-medium uppercase tracking-wider mb-1 text-right",
                    ),
                    rx.el.p(
                        f"${budget['remaining']:,.0f}",
                        class_name=f"text-sm font-bold {budget['health_color']} text-right",
                    ),
                ),
                class_name="flex justify-between mb-4 border-t border-gray-100 pt-4",
            ),
            rx.el.div(
                rx.el.button(
                    "Edit",
                    on_click=lambda: BudgetState.open_edit_budget_modal(budget),
                    class_name="text-xs font-medium text-gray-500 hover:text-indigo-600 transition-colors px-3 py-1.5 hover:bg-indigo-50 rounded-lg",
                ),
                rx.el.button(
                    rx.icon(
                        "trash-2",
                        size=14,
                        class_name="text-gray-400 group-hover:text-red-500",
                    ),
                    on_click=lambda: BudgetState.delete_budget(budget["id"]),
                    class_name="p-1.5 hover:bg-red-50 rounded-lg transition-colors group",
                ),
                class_name="flex justify-between items-center mt-2",
            ),
            class_name="p-6",
        ),
        class_name="bg-white/70 backdrop-blur-xl rounded-2xl border border-white/50 shadow-[0_8px_30px_rgb(0,0,0,0.04)] hover:shadow-[0_8px_30px_rgb(0,0,0,0.08)] transition-all duration-300 hover:-translate-y-1 group",
    )


def fab_add_budget() -> rx.Component:
    """"""

    return rx.el.button(
        rx.icon("plus", size=24, class_name="text-white"),
        on_click=BudgetState.open_add_budget_modal,
        class_name="fixed bottom-8 right-8 w-14 h-14 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-full shadow-lg shadow-indigo-300 flex items-center justify-center hover:scale-110 active:scale-95 transition-all duration-300 z-50 animate-bounce-in",
        title="Add New Budget",
    )


def budgets_page() -> rx.Component:
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
                                "Budgets",
                                class_name="text-3xl font-bold text-gray-900 tracking-tight",
                            ),
                            rx.el.p(
                                "Manage your spending limits and track utilization.",
                                class_name="text-gray-500 mt-2 text-lg",
                            ),
                        ),
                        class_name="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-10",
                    ),
                    rx.cond(
                        BudgetState.budget_stats.length() > 0,
                        rx.el.div(
                            rx.foreach(BudgetState.budget_stats, budget_card),
                            class_name="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6 animate-in fade-in slide-in-from-bottom-8 duration-700",
                        ),
                        empty_state(
                            icon="wallet",
                            title="No budgets found",
                            description="Start by creating a budget for a department, project, or category to track your spending.",
                            action_label="Create First Budget",
                            on_click=BudgetState.open_add_budget_modal,
                        ),
                    ),
                    budget_modal(),
                    fab_add_budget(),
                    class_name="max-w-7xl mx-auto relative z-10",
                ),
                class_name="flex-1 p-6 md:p-8 overflow-y-auto scroll-smooth",
            ),
            class_name="flex-1 flex flex-col h-screen overflow-hidden",
        ),
        class_name="flex h-screen bg-gray-50 font-['Inter']",
    )
