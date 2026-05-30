""""""

import typing

import reflex as rx

from lemonade_stand.ui.states.budget_state import Expense


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


def expense_row(expense: Expense) -> rx.Component:
    """"""
    return rx.el.tr(
        rx.el.td(
            rx.el.div(
                rx.el.span(
                    expense.date,
                    class_name="text-sm font-medium text-gray-900 dark:text-gray-100",
                ),
                rx.cond(
                    expense.recurring_flag,
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
                    expense.has_source_file,
                    rx.el.div(
                        rx.icon("paperclip", size=12, class_name="text-gray-400"),
                        class_name="ml-2",
                        title=expense.source_file,
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
                    expense.category,
                    class_name="text-sm text-gray-700 dark:text-gray-300",
                ),
                class_name="flex items-center",
            ),
            class_name="px-6 py-4 whitespace-nowrap",
        ),
        rx.el.td(
            rx.el.span(
                f"${expense.amount:,.2f}",
                class_name="text-sm font-semibold text-gray-900 dark:text-gray-100",
            ),
            class_name="px-6 py-4 whitespace-nowrap",
        ),
        rx.el.td(
            rx.el.span(
                expense.payment_type,
                class_name="text-sm text-gray-500 dark:text-gray-400",
            ),
            class_name="px-6 py-4 whitespace-nowrap",
        ),
        rx.el.td(
            rx.el.div(
                rx.el.span(
                    expense.description,
                    class_name="text-sm text-gray-500 dark:text-gray-400 max-w-[200px] truncate block",
                ),
                rx.cond(
                    expense.location.length() > 0,  # type: ignore
                    rx.el.div(
                        rx.foreach(
                            expense.location,
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
            status_badge(expense.exclude_flag),
            class_name="px-6 py-4 whitespace-nowrap",
        ),
        class_name="hover:bg-gray-50 dark:hover:bg-gray-700/30 transition-colors even:bg-gray-50/50 dark:even:bg-gray-800/30",
    )


def expenses_table(expense_data: list[Expense]) -> rx.Component:
    """"""
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
            expense_data.length() > 0,  # type: ignore
            rx.el.div(
                rx.el.table(
                    rx.el.thead(
                        rx.el.tr(
                            rx.el.th(
                                "Date",
                                class_name="px-6 py-4 text-left text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider",
                            ),
                            rx.el.th(
                                "Category",
                                class_name="px-6 py-4 text-left text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider",
                            ),
                            rx.el.th(
                                "Amount",
                                class_name="px-6 py-4 text-left text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider",
                            ),
                            rx.el.th(
                                "Payment Type",
                                class_name="px-6 py-4 text-left text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider",
                            ),
                            rx.el.th(
                                "Description",
                                class_name="px-6 py-4 text-left text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider",
                            ),
                            rx.el.th(
                                "Status",
                                class_name="px-6 py-4 text-left text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider",
                            ),
                            class_name="bg-gray-50/50 dark:bg-gray-800/50 border-b border-gray-100 dark:border-gray-700/50",
                        )
                    ),
                    rx.el.tbody(
                        rx.foreach(expense_data, lambda e, _: expense_row(e)),
                        class_name="bg-white/50 dark:bg-transparent divide-y divide-gray-100 dark:divide-gray-700/50",
                    ),
                    class_name="min-w-full divide-y divide-gray-200 dark:divide-gray-700/50",
                ),
                class_name="overflow-x-auto rounded-xl border border-gray-100/50 dark:border-gray-700/50",
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
        class_name="bg-white/70 dark:bg-gray-800/50 backdrop-blur-xl p-6 rounded-2xl border border-white/50 dark:border-gray-700/50 shadow-[0_8px_30px_rgb(0,0,0,0.04)]",
    )
