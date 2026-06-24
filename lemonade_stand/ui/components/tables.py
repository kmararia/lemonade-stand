""""""

import typing

import reflex as rx

from lemonade_stand.ui.states.expense_state import Expense
from lemonade_stand.ui.states.expense_state import ExpenseState
from lemonade_stand.ui.states.expense_state import ExpenseVariance


def table_row(table: Expense) -> rx.Component:
    """"""

    def status_badge(status: bool) -> rx.Component:
        """"""
        return typing.cast(
            rx.Component,
            rx.match(
                status,
                (
                    True,
                    rx.el.span(
                        "Include",
                        class_name="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400",
                    ),
                ),
                (
                    False,
                    rx.el.span(
                        "Exclude",
                        class_name="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400",
                    ),
                ),
                rx.el.span(
                    status,
                    class_name="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300",
                ),
            ),
        )

    return rx.el.tr(
        rx.el.td(
            rx.el.div(
                rx.el.span(
                    table.date,
                    class_name="text-sm font-medium text-gray-900 dark:text-gray-100",
                ),
                rx.cond(
                    table.recurring_flag,
                    rx.el.div(
                        rx.icon(
                            "repeat",
                            size=12,
                            class_name="text-indigo-500 dark:text-cyan-400",
                        ),
                        class_name="ml-2 p-1 bg-indigo-50 dark:bg-cyan-900/30 rounded-full",
                    ),
                ),
                rx.cond(
                    table.has_source_file,
                    rx.el.div(
                        rx.icon("paperclip", size=12, class_name="text-gray-400"),
                        class_name="ml-2",
                        title=table.source_file,
                    ),
                ),
                class_name="flex items-center",
            ),
            class_name="px-6 py-4 whitespace-nowrap",
        ),
        rx.el.td(
            rx.el.div(
                rx.icon("tag", size=14, class_name="mr-2 text-gray-400"),
                rx.el.span(
                    table.category,
                    class_name="text-sm text-gray-700 dark:text-gray-300",
                ),
                class_name="flex items-center",
            ),
            class_name="px-6 py-4 whitespace-nowrap",
        ),
        rx.el.td(
            rx.el.span(
                f"${table.amount:,.2f}",
                class_name="text-sm font-semibold text-gray-900 dark:text-gray-100",
            ),
            class_name="px-6 py-4 whitespace-nowrap",
        ),
        rx.el.td(
            rx.el.span(
                table.payment_type,
                class_name="text-sm text-gray-500 dark:text-gray-400",
            ),
            class_name="px-6 py-4 whitespace-nowrap",
        ),
        rx.el.td(
            rx.el.div(
                rx.el.span(
                    table.description,
                    class_name="text-sm text-gray-500 dark:text-gray-400 max-w-[200px] truncate block",
                ),
                rx.cond(
                    table.location.length() > 0,  # type: ignore
                    rx.el.div(
                        rx.foreach(
                            table.location,
                            lambda tag: rx.el.span(
                                tag,
                                class_name="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-medium bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300",
                            ),
                        ),
                        class_name="flex gap-1 mt-1 flex-wrap",
                    ),
                ),
                class_name="flex flex-col",
            ),
            class_name="px-6 py-4",
        ),
        rx.el.td(
            status_badge(table.exclude_flag),
            class_name="px-6 py-4 whitespace-nowrap",
        ),
        rx.el.td(
            rx.el.button(
                rx.icon("pencil", size=16),
                on_click=lambda: ExpenseState.open_edit_modal(
                    {
                        "index": table.date,
                        "date": table.date,
                        "category": table.category,
                        "amount": table.amount,
                        "payment_type": table.payment_type,
                        "description": table.description,
                        "exclude_flag": table.exclude_flag,
                    }
                ),
                class_name="text-gray-400 hover:text-indigo-600 dark:hover:text-cyan-400 hover:bg-indigo-50 dark:hover:bg-cyan-900/30 rounded-lg transition-all",
            ),
            class_name="pr-6 py-4 whitespace-nowrap text-right",
        ),
        class_name="hover:bg-gray-50 dark:hover:bg-gray-700/30 transition-colors even:bg-gray-50/50 dark:even:bg-gray-800/30",
    )


def data_table(edit_modal_func: typing.Callable) -> rx.Component:
    """"""

    def sortable_header(label: str, sort_key: str) -> rx.Component:
        """A reusable, clickable header for sorting columns."""

        th_class = """
            sticky top-0 z-10 px-6 py-4 text-left text-xs font-semibold
            text-gray-500 dark:text-gray-400 uppercase tracking-wider
            bg-gray-50/90 dark:bg-gray-800/90 backdrop-blur-md shadow-sm
            border-b border-gray-200 dark:border-gray-700
        """

        if label == "":
            return rx.el.th(class_name=th_class)  # Empty header for action buttons

        return rx.el.th(
            rx.el.div(
                rx.el.span(label),
                rx.icon(
                    "arrow-up-down",
                    size=14,
                    class_name="ml-1.5 text-gray-300 dark:text-gray-600 group-hover:text-indigo-500 dark:group-hover:text-cyan-400 transition-colors",
                ),
                class_name="flex items-center group cursor-pointer select-none",
                # Run backend sorting logic when header is clicked
                on_click=ExpenseState.toggle_table_sort(sort_key),
            ),
            class_name=th_class,
        )

    return rx.el.div(
        rx.el.div(
            rx.el.h3(
                "Recent Expenses",
                class_name="text-lg font-bold text-gray-900 dark:text-gray-100",
            ),
            rx.el.a(
                "View All",
                href="/expenses",
                class_name="text-sm font-medium text-indigo-600 dark:text-cyan-400 hover:text-indigo-800 transition-colors bg-indigo-50 dark:bg-cyan-900/30 px-3 py-1 rounded-lg",
            ),
            class_name="flex items-center justify-between mb-6",
        ),
        rx.cond(
            ExpenseState.expense_rows.length() > 0,
            rx.el.div(
                rx.el.table(
                    rx.el.thead(
                        rx.el.tr(
                            sortable_header(label="Date", sort_key="date"),
                            sortable_header(label="Category", sort_key="category"),
                            sortable_header(label="Amount", sort_key="amount"),
                            sortable_header(
                                label="Payment Type", sort_key="payment_type"
                            ),
                            sortable_header(
                                label="Description", sort_key="description"
                            ),
                            sortable_header(label="Status", sort_key="exclude_flag"),
                            sortable_header(label="", sort_key=""),
                            class_name="bg-gray-50/50 dark:bg-gray-800/50 border-b border-gray-100 dark:border-gray-700/50",
                        )
                    ),
                    rx.el.tbody(
                        rx.foreach(ExpenseState.expense_rows, table_row),
                        class_name="bg-white/50 dark:bg-transparent divide-y divide-gray-100 dark:divide-gray-700/50",
                    ),
                    class_name="min-w-full divide-y divide-gray-200 dark:divide-gray-700/50",
                ),
                class_name="overflow-x-auto overflow-y-auto max-h-[550px] rounded-xl border border-gray-100/50 dark:border-gray-700/50 custom-scrollbar",
            ),
            rx.el.div(
                rx.el.div(
                    rx.icon(
                        "receipt",
                        size=48,
                        class_name="text-gray-300 dark:text-gray-600 mb-3 mx-auto",
                    ),
                    rx.el.p(
                        "No expenses recorded yet.",
                        class_name="text-gray-500 dark:text-gray-400 font-medium",
                    ),
                    class_name="text-center py-12",
                ),
                class_name="bg-gray-50/30 dark:bg-gray-800/30 rounded-xl border-2 border-dashed border-gray-200 dark:border-gray-700",
            ),
        ),
        edit_modal_func(),
        class_name="bg-white/70 dark:bg-gray-800/50 backdrop-blur-xl p-6 rounded-2xl border border-white/50 dark:border-gray-700/50 shadow-[0_8px_30px_rgb(0,0,0,0.04)]",
    )


def budget_variance_table(
    title: str, table_data: rx.Var[list[ExpenseVariance]], totals_dict: rx.Var[dict]
) -> rx.Component:
    """A detailed budget variance table"""

    th_comp_class = "px-3 pb-2 font-bold text-gray-800 dark:text-gray-200"
    td_comp_class = "px-3 py-1.5 text-gray-700 dark:text-gray-300 border-b border-gray-100 dark:border-gray-700/50"
    tb_comp_class = "italic px-3 py-2"

    def render_row(item: ExpenseVariance) -> rx.Component:
        """"""

        return rx.el.tr(
            rx.el.td(
                item.category,
                class_name="""
                    font-bold text-left pl-3 pr-2 py-1.5
                    bg-[#f3dfc1] dark:bg-orange-900/30 text-gray-900 dark:text-gray-100
                    border-b-[3px] border-r-[3px] border-white dark:border-gray-800
                """,
            ),
            rx.el.td(f"{item.spent_amount:,.2f}", class_name=td_comp_class),
            rx.el.td(f"{item.allocated_amount:,.2f}", class_name=td_comp_class),
            rx.el.td(
                f"{item.utilization:,.0f}%",
                class_name=(
                    f"""{td_comp_class}
                    {
                        rx.cond(
                            item.utilization <= 50,
                            "text-green-600 dark:text-green-400",
                            rx.cond(
                                item.utilization <= 100,
                                "text-yellow-600 dark:text-yellow-400",
                                "text-red-500 dark:text-red-500",
                            ),
                        )
                    }
                    """
                ),
            ),
            rx.el.td(f"{item.remaining_amount:,.2f}", class_name=td_comp_class),
            rx.el.td(f"{item.excess_amount:,.2f}", class_name=td_comp_class),
            class_name="hover:bg-gray-50/50 dark:hover:bg-gray-700/30 transition-colors",
        )

    return rx.el.div(
        # Header
        rx.el.h2(
            title,
            class_name="text-[21px] font-bold text-[#c75d2c] dark:text-orange-500 mb-4 tracking-tight",
        ),
        # Table Container
        rx.el.div(
            rx.el.table(
                # Table Head
                rx.el.thead(
                    rx.el.tr(
                        rx.el.th("", class_name="pb-2"),  # Empty corner
                        rx.el.th("Spent", class_name=th_comp_class),
                        rx.el.th("Planned", class_name=th_comp_class),
                        rx.el.th("%Util", class_name=th_comp_class),
                        rx.el.th("Remaining", class_name=th_comp_class),
                        rx.el.th("Excess", class_name=th_comp_class),
                        class_name="border-b-2 border-gray-300 dark:border-gray-600",
                    )
                ),
                # Table Body
                rx.el.tbody(
                    rx.el.tr(
                        rx.el.td(
                            "Total",
                            class_name=(tb_comp_class + " text-left font-medium"),
                        ),
                        rx.el.td(totals_dict["spent_amount"], class_name=tb_comp_class),  # type: ignore
                        rx.el.td(
                            totals_dict["allocated_amount"],  # type: ignore
                            class_name=tb_comp_class,
                        ),
                        rx.el.td("", class_name=tb_comp_class),
                        rx.el.td(
                            totals_dict["remaining_amount"],  # type: ignore
                            class_name=tb_comp_class,
                        ),
                        rx.el.td(
                            totals_dict["excess_amount"],  # type: ignore
                            class_name=tb_comp_class,
                        ),
                        class_name="text-slate-500 dark:text-slate-400 border-b border-gray-200 dark:border-gray-700/50",
                    ),
                    rx.foreach(table_data, lambda item: render_row(item)),
                ),
                class_name="w-full text-sm text-right whitespace-nowrap",
            ),
            class_name="max-h-[350px] overflow-x-auto custom-scrollbar",
        ),
        class_name="bg-white/70 dark:bg-gray-800/50 backdrop-blur-xl p-6 rounded-2xl border border-white/50 dark:border-gray-700/50 shadow-[0_8px_30px_rgb(0,0,0,0.04)] w-full h-full",
    )
