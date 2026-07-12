""""""

import typing

import reflex as rx

from lemonade_stand.ui.states.data_state import DataRow
from lemonade_stand.ui.states.data_state import DataVariance


def table_row(table: DataRow, on_edit: typing.Callable) -> rx.Component:
    """"""

    def status_badge(status: bool) -> rx.Component:
        """"""

        base_class = (
            "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
        )

        return typing.cast(
            rx.Component,
            rx.match(
                status,
                (
                    True,
                    rx.el.span(
                        "Include",
                        class_name=f"{base_class} bg-[var(--healthy-bg)] text-[var(--healthy-text)]",
                    ),
                ),
                (
                    False,
                    rx.el.span(
                        "Exclude",
                        class_name=f"{base_class} bg-[var(--critical-bg)] text-[var(--critical-text)]",
                    ),
                ),
                rx.el.span(
                    "Unknown",
                    class_name=f"{base_class} bg-[var(--warning-bg)] text-[var(--warning-text)]",
                ),
            ),
        )

    return rx.el.tr(
        rx.el.td(
            rx.el.div(
                rx.el.span(
                    table.date,
                    class_name="text-sm font-medium text-[var(--text-main)]",
                ),
                rx.cond(
                    table.recurring_flag,
                    rx.el.div(
                        rx.icon(
                            "repeat",
                            size=12,
                            class_name="text-[var(--critical-text)]",
                        ),
                        class_name="ml-2 p-1 bg-[var(--critical-bg)] rounded-full",
                    ),
                ),
                rx.cond(
                    table.has_source_file,
                    rx.el.div(
                        rx.icon(
                            "paperclip", size=12, class_name="text-[var(--text-muted)]"
                        ),
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
                rx.icon("tag", size=14, class_name="mr-2 text-[var(--text-muted)]"),
                rx.el.span(
                    table.category,
                    class_name="text-sm text-[var(--text-main)]",
                ),
                class_name="flex items-center",
            ),
            class_name="px-6 py-4 whitespace-nowrap",
        ),
        rx.el.td(
            rx.el.span(
                f"${table.amount:,.2f}",
                class_name="text-sm font-semibold text-[var(--text-main)]",
            ),
            class_name="px-6 py-4 whitespace-nowrap",
        ),
        rx.el.td(
            rx.el.span(
                table.payment_type,
                class_name="text-sm text-[var(--text-main)]",
            ),
            class_name="px-6 py-4 whitespace-nowrap",
        ),
        rx.el.td(
            rx.el.div(
                rx.el.span(
                    table.description,
                    class_name="text-sm text-[var(--text-main)] max-w-[200px] truncate block",
                ),
                rx.cond(
                    table.location.length() > 0,  # type: ignore
                    rx.el.div(
                        rx.foreach(
                            table.location,
                            lambda tag: rx.el.span(
                                tag,
                                class_name="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-medium bg-[var(--bg-card)] text-[var(--text-main)]",
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
                on_click=lambda: on_edit(
                    {
                        "index": table.index,
                        "date": table.date,
                        "category": table.category,
                        "amount": table.amount,
                        "payment_type": table.payment_type,
                        "description": table.description,
                        "exclude_flag": table.exclude_flag,
                    }
                ),
                class_name="text-[var(--text-main)] hover:text-[var(--selected-color)] rounded-lg transition-all",
            ),
            class_name="pr-6 py-4 whitespace-nowrap text-right",
        ),
        class_name="hover:bg-[var(--bg-subtle)] even:bg-[var(--bg-card)] transition-colors",
    )


def data_table(
    title: str,
    view_all_href: str,
    rows: rx.Var,
    on_sort: typing.Callable,
    on_edit: typing.Callable,
    edit_modal_func: typing.Callable,
) -> rx.Component:
    """"""

    def sortable_header(label: str, sort_key: str) -> rx.Component:
        """A reusable, clickable header for sorting columns."""

        th_class = """
            sticky top-0 z-10 px-6 py-4 tracking-wider
            font-semibold font-bold
            text-left text-sm text-[var(--text-main)] uppercase
            bg-[var(--bg-header)] backdrop-blur-md shadow-sm
            border-b border-[var(--border-main)]
        """

        if label == "":
            return rx.el.th(class_name=th_class)  # Empty header for action buttons

        return rx.el.th(
            rx.el.div(
                rx.el.span(label),
                rx.icon(
                    "arrow-up-down",
                    size=14,
                    class_name="ml-1.5 text-[var(--text-muted)] group-hover:text-[var(--selected-color)] transition-colors",
                ),
                class_name="flex items-center group cursor-pointer select-none",
                on_click=on_sort(
                    sort_key
                ),  # Run backend sorting logic when header is clicked
            ),
            class_name=th_class,
        )

    return rx.el.div(
        rx.el.div(
            rx.el.h3(
                title,
                class_name="text-lg font-bold text-[var(--text-main)]",
            ),
            rx.el.a(
                "View All",
                href=view_all_href,
                class_name="""
                    font-medium text-sm text-[var(--healthy-text)] hover:text-[var(--warning-text)]
                    bg-[var(--healthy-bg)] hover:bg-[var(--warning-bg)]
                    transition-colors px-3 py-1 rounded-lg
                """,
            ),
            class_name="flex items-center justify-between mb-6",
        ),
        rx.cond(
            rows.length() > 0,  # type: ignore
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
                            class_name="bg-[var(--bg-subtle)] border-b border-[var(--border-subtle)]",
                        )
                    ),
                    rx.el.tbody(
                        rx.foreach(
                            rows, lambda row: table_row(table=row, on_edit=on_edit)
                        ),
                        class_name="bg-[var(--bg-card)] divide-y divide-[var(--border-subtle)]",
                    ),
                    class_name="min-w-full divide-y divide-[var(--border-subtle)]",
                ),
                class_name="overflow-x-auto overflow-y-auto max-h-[550px] rounded-xl border border-[var(--border-subtle)] custom-scrollbar",
            ),
            rx.el.div(
                rx.el.div(
                    rx.icon(
                        "receipt",
                        size=48,
                        class_name="text-[var(--text-main)] mb-3 mx-auto",
                    ),
                    rx.el.p(
                        "No transactions recorded yet.",
                        class_name="text-[var(--text-muted)] font-medium",
                    ),
                    class_name="text-center py-12",
                ),
                class_name="bg-[var(--bg-card)] rounded-xl border-2 border-dashed border-[var(--border-subtle)]",
            ),
        ),
        edit_modal_func(),
        class_name="bg-[var(--bg-card)] backdrop-blur-xl p-6 rounded-2xl border border-[var(--border-subtle)] shadow-[0_8px_30px_rgb(0,0,0,0.04)]",
    )


def budget_variance_table(
    title: str, table_data: rx.Var[list[DataVariance]], totals_dict: rx.Var[dict]
) -> rx.Component:
    """A detailed budget variance table"""

    sticky_th = (
        "sticky top-0 bg-[var(--bg-card)] border-b-[3px] border-[var(--border-subtle)]"
    )
    th_comp_class = f"{sticky_th} px-3 pb-1 font-bold text-[var(--text-main)]"
    td_comp_class = (
        "px-3 py-1.5 text-[var(--text-muted)] border-b border-[var(--border-subtle)]"
    )
    tb_comp_class = "italic px-3 py-2 text-[var(--text-muted)]"

    def render_row(item: DataVariance) -> rx.Component:
        """"""

        return rx.el.tr(
            rx.el.td(
                item.category,
                class_name="""
                    font-bold text-left pl-3 pr-2 py-1.5
                    bg-[var(--orange-color)] text-[var(--text-main)]
                    border-b-[2px] border-r-[3px] border-[var(--border-subtle)]
                """,
            ),
            rx.el.td(f"{item.spent_amount:,.2f}", class_name=td_comp_class),
            rx.el.td(f"{item.allocated_amount:,.2f}", class_name=td_comp_class),
            rx.el.td(
                f"{item.utilization:,.0f}%",
                class_name=(
                    f"""
                    {
                        rx.cond(
                            item.utilization <= 50,
                            "text-[var(--healthy-text)]",
                            rx.cond(
                                item.utilization <= 100,
                                "text-[var(--warning-text)]",
                                "text-[var(--critical-text)]",
                            ),
                        )
                    }
                    px-3 py-1.5 border-b border-[var(--border-subtle)]
                    """
                ),
            ),
            rx.el.td(f"{item.remaining_amount:,.2f}", class_name=td_comp_class),
            rx.el.td(f"{item.excess_amount:,.2f}", class_name=td_comp_class),
            class_name="hover:bg-[var(--bg-subtle)] transition-colors",
        )

    return rx.el.div(
        # Header
        rx.el.h2(
            title,
            class_name="font-bold text-[21px] text-[#c75d2c] tracking-tight mb-4",
        ),
        # Table Container
        rx.el.div(
            rx.el.table(
                # Table Head
                rx.el.thead(
                    rx.el.tr(
                        rx.el.th("", class_name=f"{sticky_th} pb-2"),  # Empty corner
                        rx.el.th("Actual", class_name=th_comp_class),
                        rx.el.th("Planned", class_name=th_comp_class),
                        rx.el.th("%Util", class_name=th_comp_class),
                        rx.el.th("Remaining", class_name=th_comp_class),
                        rx.el.th("Excess", class_name=th_comp_class),
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
                        class_name="text-[var(--text-muted)] border-b border-[var(--border-subtle)]",
                    ),
                    rx.foreach(table_data, lambda item: render_row(item)),
                ),
                class_name="text-sm text-right whitespace-nowrap w-full",
            ),
            class_name="max-h-[350px] overflow-auto custom-scrollbar",
        ),
        class_name="""
            bg-[var(--bg-card)] backdrop-blur-xl p-6 rounded-2xl
            border border-[var(--border-subtle)] shadow-[0_8px_30px_rgb(0,0,0,0.04)]
            w-full h-full
        """,
    )
