""""""

import typing

import reflex as rx

from lemonade_stand.ui.states.expense_state import TopCategory


def custom_tooltip() -> rx.Component:
    """A highly styled, reusable tooltip for all charts."""

    return rx.recharts.graphing_tooltip(
        separator="  —  ",
        animation_duration=250,
        animation_easing="ease-out",
        cursor={"fill": "var(--bg-subtle)", "opacity": 0.5},
        label_style={
            "fontWeight": "700",
            "fontSize": "13px",
            "letterSpacing": "0.5px",
            "textTransform": "uppercase",
            "marginBottom": "8px",
            "borderBottom": "1px solid var(--border-subtle)",
            "paddingBottom": "6px",
            "color": "var(--text-muted)",
        },
        item_style={
            "color": "var(--text-main)",
            "fontWeight": "600",
            "fontSize": "14px",
        },
        content_style={
            "backgroundColor": "var(--bg-card)",
            "borderRadius": "16px",
            "border": "1px solid var(--border-subtle)",
            "boxShadow": "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1)",
            "backdropFilter": "blur(16px)",
            "padding": "12px 16px",
        },
        custom_attrs={
            "formatter": rx.Var(
                """
                (value) => Number(value).toLocaleString('en-US', {
                    style: 'currency',
                    currency: 'USD',
                    minimumFractionDigits: 0,
                    maximumFractionDigits: 0
                })
            """
            )
        },
    )


def chart_view_selector(
    title_option: str,
    selected_value: str | rx.Var,
    on_change_event: rx.event.EventHandler,
) -> rx.Component:
    """"""

    return rx.el.select(
        rx.el.option(f"{title_option} Trends", value="Trend"),
        rx.el.option(f"{title_option} Distribution", value="Distribution"),
        value=selected_value,
        on_change=on_change_event,
        class_name="""
            text-xs font-medium text-[var(--text-muted)]
            bg-[var(--bg-subtle)] border-none rounded-lg
            focus:ring-1 focus:ring-[var(--selected-color)]
            py-1.5 pl-3 pr-8 cursor-pointer transition-colors
        """,
    )


def budget_chart(display_data: rx.Var[list[dict[str, typing.Any]]]) -> rx.Component:
    """"""

    def legend_item(name: str, color: str) -> rx.Component:
        """"""

        return rx.el.div(
            rx.el.div(
                class_name="w-3 h-3 rounded-full mr-2", style={"backgroundColor": color}
            ),
            rx.el.span(name, class_name="text-sm text-[var(--text-muted)]"),
            class_name="flex items-center mr-6",
        )

    def chart_legend() -> rx.Component:
        """"""

        return rx.el.div(
            legend_item("Allocated Budget", "#6366f1"),
            legend_item("Actual Spent", "#f97316"),
            class_name="flex items-center mb-4",
        )

    return rx.el.div(
        rx.el.div(
            rx.el.h3(
                "Budget vs. Actual Spend",
                class_name="text-lg font-bold text-[var(--text-main)]",
            ),
            rx.el.button(
                "Export",
                rx.icon("download", size=14, class_name="ml-2"),
                class_name="text-sm font-medium text-[var(--text-muted)] hover:text-[var(--selected-color)] flex items-center transition-colors px-3 py-1.5 hover:bg-[var(--bg-subtle)] rounded-lg",
            ),
            class_name="flex items-center justify-between mb-6",
        ),
        chart_legend(),
        rx.el.div(
            rx.recharts.responsive_container(
                rx.recharts.bar_chart(
                    rx.recharts.cartesian_grid(
                        stroke_dasharray="3 3",
                        vertical=False,
                        class_name="stroke-[var(--bg-subtle)] bg-[var(--bg-subtle)]",
                    ),
                    rx.recharts.x_axis(
                        type_="number",
                        axis_line=False,
                        tick_line=False,
                        tick={
                            "fontSize": 12,
                            "fill": "var(--text-muted)",
                            "fontWeight": 500,
                        },
                        dy=10,
                    ),
                    rx.recharts.y_axis(
                        type_="category",
                        data_key="category",
                        width=150,
                        tick={
                            "fontSize": 12,
                            "fill": "var(--text-muted)",
                            "fontWeight": 500,
                        },
                    ),
                    rx.recharts.bar(
                        data_key="allocated_amount",
                        name="Allocated Budget",
                        fill="#6366f1",
                        radius=[0, 6, 6, 0],
                        bar_size=9,
                    ),
                    rx.recharts.bar(
                        data_key="spent_amount",
                        name="Actual Spent",
                        fill="#f97316",
                        radius=[0, 6, 6, 0],
                        bar_size=9,
                    ),
                    custom_tooltip(),
                    data=display_data,
                    bar_gap=0,
                    layout="vertical",
                    bar_category_gap="30%",
                    margin={"top": 10, "right": 0, "left": -8, "bottom": -10},
                ),
                width="100%",
                height=340,
            ),
            class_name="w-full h-[340px]",
        ),
        class_name="bg-[var(--bg-card)] backdrop-blur-xl p-6 rounded-2xl border border-[var(--border-subtle)] shadow-[0_8px_30px_rgb(0,0,0,0.04)] w-full",
    )


def trend_chart(
    title: str,
    max_lines: int,
    monthly_trends: rx.Var[list[dict]],
    trend_lines: rx.Var[list[TopCategory]],
    header_action: rx.Component | None = None,
) -> rx.Component:
    """"""

    header_action: rx.Component = header_action or rx.fragment()

    return rx.el.div(
        rx.el.div(
            rx.el.h3(
                title,
                class_name="text-lg font-bold text-[var(--text-main)] mb-6",
            ),
            header_action,
            class_name="flex items-center justify-between mb-6",
        ),
        rx.el.div(
            rx.recharts.bar_chart(
                rx.recharts.cartesian_grid(
                    stroke_dasharray="3 3",
                    vertical=False,
                    class_name="stroke-[var(--border-subtle)]",
                ),
                rx.recharts.x_axis(
                    data_key="date",
                    tick={"fontSize": 12, "fill": "var(--text-muted)"},
                    dy=10,
                ),
                rx.recharts.y_axis(
                    axis_line=False,
                    tick_line=False,
                    tick={"fontSize": 12, "fill": "var(--text-muted)"},
                ),
                custom_tooltip(),
                *[
                    rx.recharts.bar(
                        data_key=rx.cond(
                            trend_lines.length() > x,  # type: ignore
                            trend_lines[x].name,  # type: ignore
                            f"Empty_{x}",
                        ),
                        type_=rx.cond(
                            trend_lines.length() > x,  # type: ignore
                            trend_lines[x].type,  # type: ignore
                            "monotone",
                        ),
                        fill=rx.cond(
                            trend_lines.length() > x,  # type: ignore
                            trend_lines[x].stroke,  # type: ignore
                            "#000000",
                        ),
                        radius=[4, 4, 0, 0],
                    )
                    for x in range(max_lines)
                ],
                data=monthly_trends,
                width="100%",
                height=300,
            ),
            class_name="w-full h-[340px]",
        ),
        class_name="bg-[var(--bg-card)] backdrop-blur-xl pt-6 px-6 rounded-2xl border border-[var(--border-subtle)] shadow-sm w-full",
    )


def pie_chart(
    title: str,
    pie_data: rx.Var[list[dict[str, typing.Any]]],
    header_action: rx.Component | None = None,
) -> rx.Component:
    """"""

    header_action: rx.Component = header_action or rx.fragment()
    pie_colors: list[str] = [
        "#6366f1",
        "#f97316",
        "#10b981",
        "#3b82f6",
        "#8b5cf6",
        "#ec4899",
    ]

    def custom_pie_legend(item: dict, index: int) -> rx.Component:
        """
        Reusable component for your custom legend rows
        """
        colors: typing.Any = rx.Var.create(pie_colors)

        return rx.el.div(
            rx.el.div(
                class_name="w-3 h-3 rounded-full shrink-0",
                style={"backgroundColor": colors[index % len(pie_colors)]},
            ),
            rx.el.span(
                item["name"],
                class_name="text-xs font-medium text-[var(--text-main)]",
            ),
            class_name="flex items-center gap-2 py-1.5",
        )

    return rx.el.div(
        rx.el.div(
            rx.el.h3(
                title,
                class_name="text-lg font-bold text-[var(--text-main)] mb-6",
            ),
            header_action,
            class_name="flex items-center justify-between mb-1",
        ),
        rx.el.div(
            # Chart Column
            rx.el.div(
                rx.recharts.responsive_container(
                    rx.recharts.pie_chart(
                        rx.recharts.pie(
                            *[
                                rx.recharts.cell(fill=pie_colors[i % len(pie_colors)])
                                for i in range(len(pie_colors))
                            ],
                            rx.recharts.label_list(
                                data_key="percent_label",
                                position="outside",
                                offset=25,
                                fill="var(--text-muted)",
                                stroke="var(--text-muted)",
                                stroke_width=4,
                                style={"paintOrder": "stroke"},
                            ),
                            data=pie_data,
                            data_key="amount",
                            name_key="name",
                            cx="50%",
                            cy="50%",
                            inner_radius=0,
                            outer_radius=120,
                            label_line={
                                "stroke": "var(--text-muted)",
                                "strokeWidth": 1.5,
                            },
                            label={"fill": "transparent"},
                            animation_easing="ease-in-out",
                        ),
                        custom_tooltip(),
                        class_name="[&_text]:!text-[9px] [&_text]:!tracking-wide",
                    ),
                    width="100%",
                    height=338,
                ),
                class_name="col-span-2 h-full",
            ),
            # Legend Column
            rx.el.div(
                rx.foreach(
                    pie_data, lambda item, index: custom_pie_legend(item, index)
                ),
                class_name="col-span-1 flex flex-col justify-center pl-4 border-l border-[var(--border-subtle)] h-full",
            ),
            class_name="grid grid-cols-3 w-full items-center",
        ),
        class_name="bg-[var(--bg-card)] backdrop-blur-xl p-6 rounded-2xl border border-[var(--border-subtle)] shadow-sm w-full",
    )
