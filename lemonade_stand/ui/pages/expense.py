""""""

import reflex as rx

from lemonade_stand.ui.components.charts import pie_chart
from lemonade_stand.ui.components.charts import trend_chart
from lemonade_stand.ui.components.date_picker import date_picker
from lemonade_stand.ui.components.header import header
from lemonade_stand.ui.components.sidebar import sidebar
from lemonade_stand.ui.components.tables import data_table
from lemonade_stand.ui.states.expense_state import STROKE_COLORS
from lemonade_stand.ui.states.expense_state import ExpenseState
from lemonade_stand.ui.states.expense_state import TopExpense


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
                    class_name="text-xl font-bold text-gray-900 dark:text-gray-100 tracking-tight",
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


def top_spenders_widget() -> rx.Component:
    """"""

    def top_spender_row(category: TopExpense) -> rx.Component:
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
                    class_name="text-sm font-semibold text-gray-900 dark:text-gray-100",
                ),
                class_name="flex items-center flex-1",
            ),
            rx.el.div(
                rx.el.p(
                    f"${category.amount:,.0f}",
                    class_name="text-sm font-bold text-gray-900 dark:text-gray-100",
                ),
                rx.el.p(
                    "Total Spend",
                    class_name="text-[10px] text-gray-400 font-medium text-right",
                ),
                class_name="text-right",
            ),
            class_name="flex items-center justify-between py-3 px-2 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors border-b border-gray-50 dark:border-gray-700/50 last:border-0",
        )

    return rx.el.div(
        rx.el.h3(
            "Top Spending Category",
            class_name="text-lg font-bold text-gray-900 dark:text-gray-100 mb-4",
        ),
        rx.el.div(
            rx.foreach(ExpenseState.top_spending_category_list, top_spender_row),
            class_name="flex flex-col",
        ),
        class_name="bg-white/70 dark:bg-gray-800/50 backdrop-blur-xl p-6 rounded-2xl border border-gray-50 dark:border-gray-700/50 shadow-sm h-full",
    )


def expense_page() -> rx.Component:
    """Expense tracking page."""

    return rx.el.div(
        # Inner floating APP
        rx.el.div(
            header(),
            rx.el.div(
                sidebar(),
                rx.el.main(
                    rx.el.div(
                        rx.el.div(
                            rx.el.h2(
                                "Expense Overview",
                                class_name="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2",
                            ),
                            date_picker(),
                            class_name="flex justify-between items-center w-full mb-6 animate-in fade-in slide-in-from-bottom-4 duration-700",
                        ),
                        rx.el.div(
                            summary_stat(
                                "Total Spent this Period",
                                f"${ExpenseState.total_expenses:,.2f}",
                                "+12% vs last year",
                                icon="dollar-sign",
                                icon_color="blue",
                            ),
                            summary_stat(
                                "Remaining Budget",
                                f"${ExpenseState.remaining_budget:,.2f}",
                                f"{100 - ExpenseState.utilization_percentage:.0f}% of total",
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
                                trend_chart(
                                    title="Spending Trends",
                                    max_lines=len(STROKE_COLORS),
                                    monthly_trends=ExpenseState.spending_trends_data,
                                    trend_lines=ExpenseState.top_spending_category_list,
                                ),
                                class_name="lg:col-span-2",
                            ),
                            rx.el.div(
                                top_spenders_widget(), class_name="lg:col-span-1"
                            ),
                            class_name="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8 animate-in fade-in slide-in-from-bottom-7 duration-700",
                        ),
                        rx.el.div(
                            rx.el.div(
                                pie_chart(
                                    title="Spending Distribution",
                                    pie_data=ExpenseState.expense_distribution_data,
                                ),
                                class_name="lg:col-span-2",
                            ),
                            # rx.el.div(distribution_chart(), class_name="lg:col-span-1"),
                            class_name="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8 animate-in fade-in slide-in-from-bottom-8 duration-700",
                        ),
                        rx.el.div(
                            rx.el.div(
                                data_table(),
                                class_name="lg:col-span-3",
                            ),
                            class_name="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8 animate-in fade-in slide-in-from-bottom-9 duration-700 delay-250",
                        ),
                        class_name="w-full mx-auto relative z-10",
                    ),
                    class_name="flex-1 p-6 md:p-8 overflow-y-auto scroll-smooth",
                ),
                class_name="flex-1 flex overflow-hidden",
            ),
            class_name="flex flex-col w-full h-full bg-gray-100 dark:bg-gray-950 text-gray-900 dark:text-gray-300 rounded-[2.5rem] shadow-2xl overflow-hidden border border-gray-100 dark:border-gray-800",
        ),
        # Grayed out bakground
        class_name="flex h-screen w-screen bg-gray-300/60 dark:bg-gray-900 p-4 md:p-6 lg:p-8",
    )
