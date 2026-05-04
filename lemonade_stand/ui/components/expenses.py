""""""

import reflex as rx

from lemonade_stand.ui.states.budget_state import BudgetState
from lemonade_stand.ui.states.budget_state import Expense


def status_badge(status: str) -> rx.Component:
    """"""
    return rx.match(
        status,
        (
            "Approved",
            rx.el.span(
                "Approved",
                class_name="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800",
            ),
        ),
        (
            "Pending",
            rx.el.span(
                "Pending",
                class_name="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800",
            ),
        ),
        (
            "Rejected",
            rx.el.span(
                "Rejected",
                class_name="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800",
            ),
        ),
        rx.el.span(
            status,
            class_name="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800",
        ),
    )


def expense_row(expense: Expense) -> rx.Component:
    """"""
    return rx.el.tr(
        rx.el.td(
            rx.el.div(
                rx.el.span(
                    expense["date"], class_name="text-sm font-medium text-gray-900"
                ),
                rx.cond(
                    expense.get("recurring_frequency", "One-time") != "One-time",
                    rx.el.div(
                        rx.icon("repeat", size=12, class_name="text-indigo-500"),
                        class_name="ml-2 p-1 bg-indigo-50 rounded-full",
                        title=f"Recurring: {expense.get('recurring_frequency')}",
                    ),
                ),
                rx.cond(
                    expense.get("has_attachment", False),
                    rx.el.div(
                        rx.icon("paperclip", size=12, class_name="text-gray-400"),
                        class_name="ml-2",
                        title="Has Attachment",
                    ),
                ),
                class_name="flex items-center",
            ),
            class_name="px-6 py-4 whitespace-nowrap",
        ),
        rx.el.td(
            rx.el.div(
                rx.icon("tag", size=14, class_name="mr-2 text-gray-400"),
                rx.el.span(expense["category"], class_name="text-sm text-gray-700"),
                class_name="flex items-center",
            ),
            class_name="px-6 py-4 whitespace-nowrap",
        ),
        rx.el.td(
            rx.el.span(
                f"${expense['amount']:,.2f}",
                class_name="text-sm font-semibold text-gray-900",
            ),
            class_name="px-6 py-4 whitespace-nowrap",
        ),
        rx.el.td(
            rx.el.span(expense["payment_method"], class_name="text-sm text-gray-500"),
            class_name="px-6 py-4 whitespace-nowrap",
        ),
        rx.el.td(
            rx.el.div(
                rx.el.span(
                    expense["description"],
                    class_name="text-sm text-gray-500 max-w-[200px] truncate block",
                ),
                rx.cond(
                    expense.get("tags", []).length() > 0,
                    rx.el.div(
                        rx.foreach(
                            expense.get("tags", []),
                            lambda tag: rx.el.span(
                                tag,
                                class_name="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-medium bg-gray-100 text-gray-600",
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
            status_badge(expense["approval_status"]),
            class_name="px-6 py-4 whitespace-nowrap",
        ),
        class_name="hover:bg-gray-50 transition-colors even:bg-gray-50/50",
    )


def expenses_table() -> rx.Component:
    """"""
    return rx.el.div(
        rx.el.div(
            rx.el.h3("Recent Expenses", class_name="text-lg font-bold text-gray-900"),
            rx.el.a(
                "View All",
                href="/expenses",
                class_name="text-sm font-medium text-indigo-600 hover:text-indigo-800 transition-colors bg-indigo-50 px-3 py-1 rounded-lg",
            ),
            class_name="flex items-center justify-between mb-6",
        ),
        rx.cond(
            BudgetState.expenses.length() > 0,
            rx.el.div(
                rx.el.table(
                    rx.el.thead(
                        rx.el.tr(
                            rx.el.th(
                                "Date",
                                class_name="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider",
                            ),
                            rx.el.th(
                                "Category",
                                class_name="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider",
                            ),
                            rx.el.th(
                                "Amount",
                                class_name="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider",
                            ),
                            rx.el.th(
                                "Payment",
                                class_name="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider",
                            ),
                            rx.el.th(
                                "Description",
                                class_name="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider",
                            ),
                            rx.el.th(
                                "Status",
                                class_name="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider",
                            ),
                            class_name="bg-gray-50/50 border-b border-gray-100",
                        )
                    ),
                    rx.el.tbody(
                        rx.foreach(BudgetState.expenses, lambda e, _: expense_row(e)),
                        class_name="bg-white/50 divide-y divide-gray-100",
                    ),
                    class_name="min-w-full divide-y divide-gray-200",
                ),
                class_name="overflow-x-auto rounded-xl border border-gray-100/50",
            ),
            rx.el.div(
                rx.el.div(
                    rx.icon(
                        "receipt", size=48, class_name="text-gray-300 mb-3 mx-auto"
                    ),
                    rx.el.p(
                        "No expenses recorded yet.",
                        class_name="text-gray-500 font-medium",
                    ),
                    class_name="text-center py-12",
                ),
                class_name="bg-gray-50/30 rounded-xl border-2 border-dashed border-gray-200",
            ),
        ),
        class_name="bg-white/70 backdrop-blur-xl p-6 rounded-2xl border border-white/50 shadow-[0_8px_30px_rgb(0,0,0,0.04)]",
    )
