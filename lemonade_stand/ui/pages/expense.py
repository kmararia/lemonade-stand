""""""

import reflex as rx

from lemonade_stand.ui.components.charts import chart_view_selector
from lemonade_stand.ui.components.charts import pie_chart
from lemonade_stand.ui.components.charts import trend_chart
from lemonade_stand.ui.components.date_picker import date_picker
from lemonade_stand.ui.components.layout import page_layout
from lemonade_stand.ui.components.modals import generic_edit_modal
from lemonade_stand.ui.components.modals import modal_input_field
from lemonade_stand.ui.components.small_cards import summary_stats_card
from lemonade_stand.ui.components.tables import budget_variance_table
from lemonade_stand.ui.components.tables import data_table
from lemonade_stand.ui.components.widgets import activity_feed
from lemonade_stand.ui.components.widgets import top_category_widget
from lemonade_stand.ui.states.expense_state import STROKE_COLORS
from lemonade_stand.ui.states.expense_state import ExpenseState


def expense_edit_modal() -> rx.Component:
    """"""

    return generic_edit_modal(
        *[
            modal_input_field(
                label="Date",
                value=ExpenseState.edit_values["date"],
                on_change=ExpenseState.set_edit_value,
                field_name="date",
            ),
            modal_input_field(
                label="Category",
                value=ExpenseState.edit_values["category"],
                on_change=ExpenseState.set_edit_value,
                field_name="category",
                config={"select_options": ExpenseState.distinct_values["category"]},
            ),
            modal_input_field(
                label="Amount",
                value=ExpenseState.edit_values["amount"],
                on_change=ExpenseState.set_edit_value,
                field_name="amount",
                config={"input_type": "number"},
            ),
            modal_input_field(
                label="Payment Type",
                value=ExpenseState.edit_values["payment_type"],
                on_change=ExpenseState.set_edit_value,
                field_name="payment_type",
                config={"select_options": ExpenseState.distinct_values["payment"]},
            ),
            modal_input_field(
                label="Description",
                value=ExpenseState.edit_values["description"],
                on_change=ExpenseState.set_edit_value,
                field_name="description",
                config={"is_textarea": True, "col_span_2": True},
            ),
            modal_input_field(
                label="Exclude Status",
                value=ExpenseState.edit_values["exclude_flag"],
                on_change=ExpenseState.set_edit_value,
                field_name="exclude_flag",
                config={"select_options": ExpenseState.distinct_values["exclude_flag"]},
            ),
        ],
        title="Edit Expense",
        description="Make changes to this transaction. Click save when you're done.",
        on_save=ExpenseState.apply_data_edits,
        is_open=ExpenseState.is_edit_modal_open,
        on_open_change=ExpenseState.set_is_edit_modal_open,
    )


def expense_page() -> rx.Component:
    """Expense tracking page."""

    def chart_view_selector_expense() -> rx.Component:
        """"""

        return chart_view_selector(
            title_option="Spending",
            selected_value=ExpenseState.chart_view_mode,
            on_change_event=ExpenseState.set_chart_view_mode,
        )

    return page_layout(
        rx.el.div(
            rx.el.div(
                rx.el.h2(
                    "Expense Overview",
                    class_name="text-2xl font-bold text-[var(--text-main)] tracking-tight mb-2",
                ),
                date_picker(),
                class_name="flex justify-between items-center w-full mb-6 animate-in fade-in slide-in-from-bottom-4 duration-700",
            ),
            rx.el.div(
                summary_stats_card(
                    "Total Spent this Period",
                    f"${ExpenseState.total_expenses:,.2f}",
                    (
                        f"{ExpenseState.percentage_of_income_spent:.0f}% of income",
                        rx.cond(
                            ExpenseState.percentage_of_income_spent < 100,
                            "badge_check",
                            "badge_alert",
                        ),
                        rx.cond(
                            ExpenseState.percentage_of_income_spent < 100,
                            "emerald",
                            "red",
                        ),
                    ),
                    icon="dollar-sign",
                    icon_color="blue",
                ),
                summary_stats_card(
                    "Remaining Budget",
                    f"${ExpenseState.remaining_budget:,.2f}",
                    (
                        f"{ExpenseState.remaining_budget_percentage:.0f}% of total",
                        rx.cond(
                            ExpenseState.remaining_budget_percentage > 0,
                            "trending-up",
                            "trending-down",
                        ),
                        rx.cond(
                            ExpenseState.remaining_budget_percentage > 0,
                            "emerald",
                            "red",
                        ),
                    ),
                    icon="wallet",
                    icon_color="emerald",
                ),
                summary_stats_card(
                    "Top Category",
                    f"{ExpenseState.top_spending_category}",
                    ("Most active expense category", "eye", "purple"),
                    icon="tag",
                    icon_color="purple",
                ),
                summary_stats_card(
                    "Active Budgets",
                    f"{ExpenseState.active_budgets}",
                    ("Across all expenses", "layers", "orange"),
                    icon="layers",
                    icon_color="orange",
                ),
                class_name="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-5 pt-4 animate-in fade-in slide-in-from-bottom-6 duration-700",
            ),
            rx.el.div(
                rx.el.div(
                    budget_variance_table(
                        title="Expense",
                        table_data=ExpenseState.expense_variance_stats,
                        totals_dict=ExpenseState.expense_variance_totals,
                    ),
                    class_name="lg:col-span-2",
                ),
                rx.el.div(
                    top_category_widget(
                        card_title="Top Spending Categories",
                        amount_title="Total Spent",
                        top_category_list=ExpenseState.top_spending_category_list,
                    ),
                    class_name="lg:col-span-1",
                ),
                class_name="grid grid-cols-1 lg:grid-cols-3 gap-5 mb-5 animate-in fade-in slide-in-from-bottom-7 duration-700",
            ),
            rx.el.div(
                rx.el.div(
                    rx.match(
                        ExpenseState.chart_view_mode,
                        (
                            "Trend",
                            trend_chart(
                                title="Spending Trends",
                                max_lines=len(STROKE_COLORS),
                                monthly_trends=ExpenseState.spending_trends_data,
                                trend_lines=ExpenseState.top_spending_category_list,
                                header_action=chart_view_selector_expense(),
                            ),
                        ),
                        (
                            "Distribution",
                            pie_chart(
                                title="Spending Distribution",
                                pie_data=ExpenseState.expense_distribution_data,
                                header_action=chart_view_selector_expense(),
                            ),
                        ),
                        # Default fallback
                        trend_chart(
                            title="Spending Trends",
                            max_lines=len(STROKE_COLORS),
                            monthly_trends=ExpenseState.spending_trends_data,
                            trend_lines=ExpenseState.top_spending_category_list,
                            header_action=chart_view_selector_expense(),
                        ),
                    ),
                    class_name="lg:col-span-2 max-h-[443px]",
                ),
                rx.el.div(
                    activity_feed(
                        title="Notable Expenses",
                        transaction_list=ExpenseState.notable_transactions,
                    ),
                    class_name="lg:col-span-1 max-h-[443px] w-full",
                ),
                class_name="grid grid-cols-1 lg:grid-cols-3 gap-5 mb-5 animate-in fade-in slide-in-from-bottom-8 duration-700",
            ),
            rx.el.div(
                rx.el.div(
                    data_table(
                        title="Recent Expenses",
                        view_all_href="/expenses",
                        rows=ExpenseState.expense_rows,
                        on_sort=ExpenseState.toggle_table_sort,
                        on_edit=ExpenseState.open_edit_modal,
                        edit_modal_func=expense_edit_modal,
                    ),
                    class_name="lg:col-span-3",
                ),
                class_name="grid grid-cols-1 lg:grid-cols-3 gap-5 mb-5 animate-in fade-in slide-in-from-bottom-9 duration-700",
            ),
            class_name="w-full mx-auto relative z-10",
        ),
    )
