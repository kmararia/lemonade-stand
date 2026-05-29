""""""

import reflex as rx


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


def budget_chart(display_data) -> rx.Component:
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
            rx.recharts.bar_chart(
                rx.recharts.cartesian_grid(
                    stroke_dasharray="3 3",
                    vertical=False,
                    class_name="stroke-gray-100 dark:stroke-gray-700/50",
                ),
                rx.recharts.x_axis(
                    data_key="name",
                    axis_line=False,
                    tick_line=False,
                    tick={
                        "fontSize": 12,
                        "fill": rx.color_mode_cond("#9ca3af", "#6b7280"),
                        "fontWeight": 500,
                    },
                    dy=10,
                ),
                rx.recharts.y_axis(
                    axis_line=False,
                    tick_line=False,
                    tick={
                        "fontSize": 12,
                        "fill": rx.color_mode_cond("#9ca3af", "#6b7280"),
                        "fontWeight": 500,
                    },
                ),
                rx.recharts.tooltip(
                    cursor={"fill": rx.color_mode_cond("#f8fafc", "#374151")},
                    content_style={
                        "backgroundColor": rx.color_mode_cond(
                            "rgba(255, 255, 255, 0.9)", "rgba(31, 41, 55, 0.9)"
                        ),
                        "borderRadius": "12px",
                        "border": rx.color_mode_cond(
                            "1px solid rgba(255, 255, 255, 0.5)",
                            "1px solid rgba(55, 65, 81, 0.5)",
                        ),
                        "boxShadow": "0 10px 15px -3px rgba(0, 0, 0, 0.1)",
                        "backdropFilter": "blur(10px)",
                        "padding": "12px",
                        "color": rx.color_mode_cond("#1f2937", "#f3f4f6"),
                    },
                    item_style={
                        "color": rx.color_mode_cond("#1f2937", "#e5e7eb"),
                    },
                ),
                rx.recharts.bar(
                    data_key="allocated",
                    name="Allocated Budget",
                    fill="#6366f1",
                    radius=[6, 6, 0, 0],
                    bar_size=24,
                ),
                rx.recharts.bar(
                    data_key="spent",
                    name="Actual Spent",
                    fill="#f97316",
                    radius=[6, 6, 0, 0],
                    bar_size=24,
                ),
                data=display_data,
                height=320,
                width="100%",
                margin={"top": 10, "right": 0, "left": -20, "bottom": 0},
            ),
            class_name="w-full h-[320px]",
        ),
        class_name="bg-white/70 dark:bg-gray-800/50 backdrop-blur-xl p-8 rounded-2xl border border-white/50 dark:border-gray-700/50 shadow-[0_8px_30px_rgb(0,0,0,0.04)] w-full",
    )
