""""""

import reflex as rx

from lemonade_stand.ui.components.charts import pie_chart
from lemonade_stand.ui.components.charts import trend_chart
from lemonade_stand.ui.components.date_picker import date_picker
from lemonade_stand.ui.components.header import header
from lemonade_stand.ui.components.modals import generic_edit_modal
from lemonade_stand.ui.components.modals import modal_input_field
from lemonade_stand.ui.components.sidebar import sidebar
from lemonade_stand.ui.components.small_cards import summary_stats_card
from lemonade_stand.ui.components.tables import budget_variance_table
from lemonade_stand.ui.components.tables import data_table
from lemonade_stand.ui.components.widgets import activity_feed
from lemonade_stand.ui.components.widgets import top_category_widget
from lemonade_stand.ui.states.income_state import STROKE_COLORS
from lemonade_stand.ui.states.income_state import IncomeState


def chart_view_selector() -> rx.Component:
    """"""

    return rx.el.select(
        rx.el.option("Income Trends", value="Trend"),
        rx.el.option("Income Distribution", value="Distribution"),
        value=IncomeState.chart_view_mode,
        on_change=IncomeState.set_chart_view_mode,
        class_name="""
            text-xs font-medium text-gray-600 dark:text-gray-400
            bg-gray-50 dark:bg-gray-800 border-none rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700
            focus:ring-1 focus:ring-indigo-500 py-1.5 pl-3 pr-8 cursor-pointer transition-colors
        """,
    )


def income_edit_modal() -> rx.Component:
    """"""

    return generic_edit_modal(
        *[
            modal_input_field(
                label="Date",
                value=IncomeState.edit_values["date"],
                on_change=IncomeState.set_edit_value,
                field_name="date",
            ),
            modal_input_field(
                label="Category",
                value=IncomeState.edit_values["category"],
                on_change=IncomeState.set_edit_value,
                field_name="category",
                config={"select_options": IncomeState.distinct_values["category"]},
            ),
            modal_input_field(
                label="Amount",
                value=IncomeState.edit_values["amount"],
                on_change=IncomeState.set_edit_value,
                field_name="amount",
                config={"input_type": "number"},
            ),
            modal_input_field(
                label="Payment Type",
                value=IncomeState.edit_values["payment_type"],
                on_change=IncomeState.set_edit_value,
                field_name="payment_type",
                config={"select_options": IncomeState.distinct_values["payment"]},
            ),
            modal_input_field(
                label="Description",
                value=IncomeState.edit_values["description"],
                on_change=IncomeState.set_edit_value,
                field_name="description",
                config={"is_textarea": True, "col_span_2": True},
            ),
            modal_input_field(
                label="Exclude Status",
                value=IncomeState.edit_values["exclude_flag"],
                on_change=IncomeState.set_edit_value,
                field_name="exclude_flag",
                config={"select_options": IncomeState.distinct_values["exclude_flag"]},
            ),
        ],
        title="Edit Income",
        description="Make changes to this transaction. Click save when you're done.",
        on_save=IncomeState.apply_data_edits,
        is_open=IncomeState.is_edit_modal_open,
        on_open_change=IncomeState.set_is_edit_modal_open,
    )


def income_page() -> rx.Component:
    """Income tracking page."""

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
                                "Income Overview",
                                class_name="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2",
                            ),
                            date_picker(),
                            class_name="flex justify-between items-center w-full mb-6 animate-in fade-in slide-in-from-bottom-4 duration-700",
                        ),
                        rx.el.div(
                            summary_stats_card(
                                "Total Income this Period",
                                f"${IncomeState.total_earnings:,.2f}",
                                (
                                    f"{IncomeState.percentage_of_target_earned:.0f}% of target",
                                    rx.cond(
                                        IncomeState.percentage_of_target_earned >= 20,
                                        "badge_check",
                                        "badge_alert",
                                    ),
                                    rx.cond(
                                        IncomeState.percentage_of_target_earned >= 20,
                                        "emerald",
                                        "red",
                                    ),
                                ),
                                icon="dollar-sign",
                                icon_color="blue",
                            ),
                            summary_stats_card(
                                "Remaining Target",
                                f"${IncomeState.remaining_target:,.2f}",
                                (
                                    f"{IncomeState.remaining_target_percentage:.0f}% of total",
                                    rx.cond(
                                        IncomeState.remaining_target_percentage < 50,
                                        "trending-up",
                                        "trending-down",
                                    ),
                                    rx.cond(
                                        IncomeState.remaining_target_percentage < 50,
                                        "emerald",
                                        "yellow",
                                    ),
                                ),
                                icon="wallet",
                                icon_color="emerald",
                            ),
                            summary_stats_card(
                                "Top Category",
                                f"{IncomeState.top_income_category}",
                                ("Most active income category", "eye", "green"),
                                icon="tag",
                                icon_color="purple",
                            ),
                            summary_stats_card(
                                "Active Budgets",
                                f"{IncomeState.active_budgets}",
                                ("Across all income sources", "layers", "orange"),
                                icon="layers",
                                icon_color="orange",
                            ),
                            class_name="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-5 pt-4 animate-in fade-in slide-in-from-bottom-6 duration-700",
                        ),
                        rx.el.div(
                            rx.el.div(
                                budget_variance_table(
                                    title="Income",
                                    table_data=IncomeState.income_variance_stats,
                                    totals_dict=IncomeState.income_variance_totals,
                                ),
                                class_name="lg:col-span-2",
                            ),
                            rx.el.div(
                                top_category_widget(
                                    card_title="Top Earning Categories",
                                    amount_title="Total Earned",
                                    top_category_list=IncomeState.top_earning_category_list,
                                ),
                                class_name="lg:col-span-1",
                            ),
                            class_name="grid grid-cols-1 lg:grid-cols-3 gap-5 mb-5 animate-in fade-in slide-in-from-bottom-7 duration-700",
                        ),
                        rx.el.div(
                            rx.el.div(
                                rx.match(
                                    IncomeState.chart_view_mode,
                                    (
                                        "Trend",
                                        trend_chart(
                                            title="Earnings Trends",
                                            max_lines=len(STROKE_COLORS),
                                            monthly_trends=IncomeState.income_trends_data,
                                            trend_lines=IncomeState.top_earning_category_list,
                                            header_action=chart_view_selector(),  # Passing the dropdown
                                        ),
                                    ),
                                    (
                                        "Distribution",
                                        pie_chart(
                                            title="Earnings Distribution",
                                            pie_data=IncomeState.income_distribution_data,
                                            header_action=chart_view_selector(),  # Passing the dropdown
                                        ),
                                    ),
                                    # Default fallback
                                    trend_chart(
                                        title="Earnings Trends",
                                        max_lines=len(STROKE_COLORS),
                                        monthly_trends=IncomeState.income_trends_data,
                                        trend_lines=IncomeState.top_earning_category_list,
                                        header_action=chart_view_selector(),
                                    ),
                                ),
                                class_name="lg:col-span-2 max-h-[443px]",
                            ),
                            rx.el.div(
                                activity_feed(
                                    title="Notable Earnings",
                                    transaction_list=IncomeState.notable_transactions,
                                ),
                                class_name="lg:col-span-1 max-h-[443px] w-full",
                            ),
                            class_name="grid grid-cols-1 lg:grid-cols-3 gap-5 mb-5 animate-in fade-in slide-in-from-bottom-8 duration-700",
                        ),
                        rx.el.div(
                            rx.el.div(
                                data_table(
                                    title="Recent Earnings",
                                    view_all_href="/income",
                                    rows=IncomeState.income_rows,
                                    on_sort=IncomeState.toggle_table_sort,
                                    on_edit=IncomeState.open_edit_modal,
                                    edit_modal_func=income_edit_modal,
                                ),
                                class_name="lg:col-span-3",
                            ),
                            class_name="grid grid-cols-1 lg:grid-cols-3 gap-5 mb-5 animate-in fade-in slide-in-from-bottom-9 duration-700 delay-250",
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
        class_name="flex h-screen w-screen bg-gray-300/60 dark:bg-gray-900 p-4 md:p-6 lg:p-6",
    )
