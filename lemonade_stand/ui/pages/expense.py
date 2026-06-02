""""""

import reflex as rx

from lemonade_stand.ui.components.date_picker import date_picker
from lemonade_stand.ui.components.sidebar import sidebar
from lemonade_stand.ui.components.tables import data_table
from lemonade_stand.ui.states.expense_state import ExpenseState


def summary_stat(
    label: str,
    value: str,
    subtext: str = "",
    icon: str = "activity",
    icon_color: str = "indigo",
) -> rx.Component:
    """"""

    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.p(
                    label,
                    class_name="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1",
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
                    size=20,
                    class_name=f"text-{icon_color}-600 dark:text-{icon_color}-400/60 transition-colors",
                ),
                class_name=f"p-2.5 rounded-xl bg-{icon_color}-50 dark:bg-{icon_color}-900/30 group-hover:scale-110 transition-transform duration-300 shadow-sm",
            ),
            class_name="flex justify-between items-start mb-3",
        ),
        rx.cond(
            subtext != "",
            rx.el.div(
                rx.icon("trending-up", size=14, class_name="text-emerald-500 mr-1"),
                rx.el.span(
                    subtext,
                    class_name="text-xs font-medium text-gray-500 dark:text-gray-400",
                ),
                class_name="flex items-center",
            ),
            rx.el.span(class_name="hidden"),
        ),
        class_name="group bg-white/80 dark:bg-gray-800/50 backdrop-blur-sm p-6 rounded-2xl border border-gray-100 dark:border-gray-700/50 shadow-[0_8px_30px_rgb(0,0,0,0.04)] hover:shadow-[0_8px_30px_rgb(0,0,0,0.08)] transition-all duration-300 hover:-translate-y-1",
    )


def expense_page() -> rx.Component:
    """Expense tracking page."""

    return rx.el.div(
        sidebar(),
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.div(
                            rx.el.h2(
                                "Overview",
                                class_name="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2",
                            ),
                            date_picker(),
                            class_name="flex justify-between items-center w-full",
                        ),
                        rx.el.p(
                            "Track your spending, income, and budget in real-time.",
                            class_name="text-gray-600 dark:text-gray-400 mb-6",
                        ),
                        class_name="mb-6 animate-in fade-in slide-in-from-bottom-4 duration-700",
                    ),
                    rx.el.div(
                        summary_stat(
                            "Total Spent YTD",
                            f"${ExpenseState.total_expenses:,.2f}",
                            "+12% vs last year",
                            icon="dollar-sign",
                            icon_color="blue",
                        ),
                        summary_stat(
                            "Remaining Budget",
                            f"${ExpenseState.remaining_budget:,.2f}",
                            f"{100 - ExpenseState.utilization_percentage}% of total",
                            icon="wallet",
                            icon_color="emerald",
                        ),
                        summary_stat(
                            "Top Category",
                            f"{ExpenseState.top_spending_category}",
                            "Most active sector",
                            icon="tag",
                            icon_color="purple",
                        ),
                        summary_stat(
                            "Active Budgets",
                            f"{ExpenseState.active_budgets}",
                            "Across all departments",
                            icon="layers",
                            icon_color="orange",
                        ),
                        class_name="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8 animate-in fade-in slide-in-from-bottom-6 duration-700",
                    ),
                    rx.el.div(
                        rx.el.div(
                            data_table(),
                            class_name="lg:col-span-3",
                        ),
                        class_name="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8 animate-in fade-in slide-in-from-bottom-9 duration-700 delay-250",
                    ),
                    class_name="max-w-7xl mx-auto relative z-10",
                ),
                class_name="flex-1 p-6 md:p-8 overflow-y-auto scroll-smooth",
            ),
        ),
        class_name="flex h-screen bg-gray-50 dark:bg-gray-950 text-gray-900 dark:text-gray-300 font-['Inter'] selection:bg-indigo-100 dark:selection:bg-cyan-900 selection:text-indigo-900 dark:selection:text-cyan-100",
    )
