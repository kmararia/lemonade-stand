""""""

import typing

import reflex as rx

from lemonade_stand.ui.states.expense_state import TopExpense


def custom_tooltip() -> rx.Component:
    """A highly styled, reusable tooltip for all charts."""
    return rx.recharts.graphing_tooltip(
        separator="  —  ",
        animation_duration=250,
        animation_easing="ease-out",
        cursor=rx.color_mode_cond(
            {"fill": "#f8fafc", "opacity": 0.5}, {"fill": "#1f2937", "opacity": 0.5}
        ),
        label_style=rx.color_mode_cond(
            {
                "fontWeight": "700",
                "fontSize": "13px",
                "letterSpacing": "0.5px",
                "textTransform": "uppercase",
                "marginBottom": "8px",
                "borderBottom": "1px solid rgba(0, 0, 0, 0.05)",
                "paddingBottom": "6px",
                "color": "#9ca3af",
            },
            {
                "fontWeight": "700",
                "fontSize": "13px",
                "letterSpacing": "0.5px",
                "textTransform": "uppercase",
                "marginBottom": "8px",
                "borderBottom": "1px solid rgba(255, 255, 255, 0.1)",
                "paddingBottom": "6px",
                "color": "#6b7280",
            },
        ),
        item_style=rx.color_mode_cond(
            {"color": "#111827", "fontWeight": "600", "fontSize": "14px"},
            {"color": "#f9fafb", "fontWeight": "600", "fontSize": "14px"},
        ),
        content_style=rx.color_mode_cond(
            {
                "backgroundColor": "rgba(255, 255, 255, 0.85)",
                "borderRadius": "16px",
                "border": "1px solid rgba(255, 255, 255, 0.8)",
                "boxShadow": "0 20px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.01)",
                "backdropFilter": "blur(16px)",
                "padding": "12px 16px",
            },
            {
                "backgroundColor": "rgba(17, 24, 39, 0.85)",
                "borderRadius": "16px",
                "border": "1px solid rgba(255, 255, 255, 0.05)",
                "boxShadow": "0 20px 25px -5px rgba(0, 0, 0, 0.3), 0 8px 10px -6px rgba(0, 0, 0, 0.2)",
                "backdropFilter": "blur(16px)",
                "padding": "12px 16px",
            },
        ),
        custom_attrs={
            "formatter": rx.Var(
                "(value) => Number(value).toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 0 })"
            )
        },
    )


def legend_item(name: str, color: str) -> rx.Component:
    """"""

    return rx.el.div(
        rx.el.div(
            class_name="w-3 h-3 rounded-full mr-2", style={"backgroundColor": color}
        ),
        rx.el.span(name, class_name="text-sm text-gray-600 dark:text-gray-400"),
        class_name="flex items-center mr-6",
    )


def chart_legend() -> rx.Component:
    """"""

    return rx.el.div(
        legend_item("Allocated Budget", "#6366f1"),
        legend_item("Actual Spent", "#f97316"),
        class_name="flex items-center mb-4",
    )


def budget_chart(display_data: rx.Var[list[dict[str, typing.Any]]]) -> rx.Component:
    """"""

    return rx.el.div(
        rx.el.div(
            rx.el.h3(
                "Budget vs. Actual Spend",
                class_name="text-lg font-bold text-gray-900 dark:text-gray-100",
            ),
            rx.el.button(
                "Export",
                rx.icon("download", size=14, class_name="ml-2"),
                class_name="text-sm font-medium text-gray-600 dark:text-gray-400 hover:text-indigo-600 dark:hover:text-cyan-400 flex items-center transition-colors px-3 py-1.5 hover:bg-indigo-50 dark:hover:bg-cyan-900/30 rounded-lg",
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
                        class_name="stroke-gray-100 dark:stroke-gray-700/50",
                    ),
                    rx.recharts.x_axis(
                        type_="number",
                        axis_line=False,
                        tick_line=False,
                        tick=rx.color_mode_cond(
                            {"fontSize": 12, "fill": "#9ca3af", "fontWeight": 500},
                            {"fontSize": 12, "fill": "#6b7280", "fontWeight": 500},
                        ),
                        dy=10,
                    ),
                    rx.recharts.y_axis(
                        type_="category",
                        data_key="category",
                        width=150,
                        tick=rx.color_mode_cond(
                            {"fontSize": 12, "fill": "#9ca3af", "fontWeight": 500},
                            {"fontSize": 12, "fill": "#6b7280", "fontWeight": 500},
                        ),
                    ),
                    rx.recharts.bar(
                        data_key="allocated_amount",
                        name="Allocated Budget",
                        fill="#6366f1",
                        radius=[0, 6, 6, 0],
                        bar_size=10,
                    ),
                    rx.recharts.bar(
                        data_key="spent_amount",
                        name="Actual Spent",
                        fill="#f97316",
                        radius=[0, 6, 6, 0],
                        bar_size=10,
                    ),
                    custom_tooltip(),
                    data=display_data,
                    bar_gap=0,
                    layout="vertical",
                    bar_category_gap="30%",
                    margin={"top": 10, "right": 0, "left": -15, "bottom": -10},
                ),
                width="100%",
                height=340,
            ),
            class_name="w-full h-[340px]",
        ),
        class_name="bg-white/70 dark:bg-gray-800/50 backdrop-blur-xl p-8 rounded-2xl border border-white/50 dark:border-gray-700/50 shadow-[0_8px_30px_rgb(0,0,0,0.04)] w-full",
    )


def trend_chart(
    title: str,
    max_lines: int,
    monthly_trends: rx.Var[list[dict]],
    trend_lines: rx.Var[list[TopExpense]],
) -> rx.Component:
    """"""

    return rx.el.div(
        rx.el.h3(
            title, class_name="text-lg font-bold text-gray-900 dark:text-gray-100 mb-6"
        ),
        rx.el.div(
            rx.recharts.bar_chart(
                rx.recharts.cartesian_grid(
                    stroke_dasharray="3 3",
                    vertical=False,
                    class_name="stroke-gray-200 dark:stroke-gray-700/50",
                ),
                rx.recharts.x_axis(
                    data_key="date",
                    tick={"fontSize": 12, "fill": "#6b7280"},
                    dy=10,
                ),
                rx.recharts.y_axis(
                    axis_line=False,
                    tick_line=False,
                    tick={"fontSize": 12, "fill": "#6b7280"},
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
        class_name="bg-white/70 dark:bg-gray-800/50 backdrop-blur-xl p-6 rounded-2xl border border-gray-100 dark:border-gray-700/50 shadow-sm w-full",
    )


def pie_chart(
    title: str,
    pie_data: rx.Var[list[dict[str, typing.Any]]],
) -> rx.Component:
    """"""
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
                class_name="text-xs font-medium text-gray-600 dark:text-gray-400",
            ),
            class_name="flex items-center gap-2 py-1.5",
        )

    return rx.el.div(
        rx.el.h3(
            title, class_name="text-lg font-bold text-gray-900 dark:text-gray-100 mb-4"
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
                                fill=rx.color_mode_cond("#1f2937", "#e5e7eb"),
                                stroke=rx.color_mode_cond("#1f2937", "#e5e7eb"),
                                stroke_width=4,
                                style={"paintOrder": "stroke"},
                            ),
                            data=pie_data,
                            data_key="amount",
                            name_key="name",
                            cx="50%",
                            cy="50%",
                            inner_radius="0%",
                            outer_radius="80%",
                            label_line={
                                "stroke": rx.color_mode_cond("#9ca3af", "#4b5563"),
                                "strokeWidth": 1.5,
                            },
                            label={"fill": "transparent"},
                            animation_easing="ease-in-out",
                        ),
                        custom_tooltip(),
                        class_name="[&_text]:!text-[9px] [&_text]:!tracking-wide",
                    ),
                    width="100%",
                    height="100%",
                ),
                class_name="col-span-2 h-full",
            ),
            # Legend Column
            rx.el.div(
                rx.foreach(
                    pie_data, lambda item, index: custom_pie_legend(item, index)
                ),
                class_name="col-span-1 flex flex-col justify-center pl-4 border-l border-gray-50 dark:border-gray-700/30 h-full",
            ),
            class_name="grid grid-cols-3 w-full h-[300px] sm:h-[350px] lg:h-[380px] items-center",
        ),
        class_name="bg-white/70 dark:bg-gray-800/50 backdrop-blur-xl p-6 rounded-2xl border border-gray-100 dark:border-gray-700/50 shadow-sm w-full",
    )
