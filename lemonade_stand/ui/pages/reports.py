""""""

import reflex as rx

from lemonade_stand.ui.components.header import header
from lemonade_stand.ui.components.sidebar import sidebar
from lemonade_stand.ui.states.budget_state import BudgetState


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
                    class_name="text-2xl font-bold text-gray-900 dark:text-gray-100 tracking-tight",
                ),
                class_name="flex flex-col",
            ),
            rx.el.div(
                rx.icon(icon, size=20, class_name=f"text-{icon_color}-600"),
                class_name=f"p-2.5 bg-{icon_color}-50 rounded-xl",
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
        class_name="bg-white/80 backdrop-blur-sm p-5 rounded-2xl border border-gray-100 shadow-sm hover:shadow-md transition-all duration-300 hover:-translate-y-1",
    )


def legend_item(label: str, color: str) -> rx.Component:
    """"""

    return rx.el.div(
        rx.el.div(
            class_name="w-3 h-3 rounded-full mr-2", style={"backgroundColor": color}
        ),
        rx.el.span(label, class_name="text-sm text-gray-600 dark:text-gray-400"),
        class_name="flex items-center",
    )


def custom_legend() -> rx.Component:
    """"""

    return rx.el.div(
        legend_item("Marketing", "#6366f1"),
        legend_item("Engineering", "#f97316"),
        legend_item("Office Renovation", "#14b8a6"),
        legend_item("Sales", "#ec4899"),
        legend_item("HR", "#8b5cf6"),
        legend_item("Website Redesign", "#3b82f6"),
        class_name="flex flex-wrap items-center gap-4 justify-center mt-4",
    )


def trend_chart() -> rx.Component:
    """"""

    return rx.el.div(
        rx.el.h3(
            "Spending Trends",
            class_name="text-lg font-bold text-gray-900 dark:text-gray-100 mb-6",
        ),
        rx.el.div(
            rx.recharts.line_chart(
                rx.recharts.cartesian_grid(
                    stroke_dasharray="3 3", vertical=False, class_name="stroke-gray-200"
                ),
                rx.recharts.x_axis(
                    data_key="name",
                    axis_line=False,
                    tick_line=False,
                    tick={"fontSize": 12, "fill": "#6b7280"},
                    dy=10,
                ),
                rx.recharts.y_axis(
                    axis_line=False,
                    tick_line=False,
                    tick={"fontSize": 12, "fill": "#6b7280"},
                ),
                rx.recharts.tooltip(
                    cursor={"stroke": "#6366f1", "strokeWidth": 2},
                    content_style={
                        "backgroundColor": "#fff",
                        "borderRadius": "8px",
                        "border": "none",
                        "boxShadow": "0 4px 6px -1px rgb(0 0 0 / 0.1)",
                    },
                ),
                rx.recharts.line(
                    data_key="Marketing",
                    stroke="#6366f1",
                    stroke_width=2,
                    dot=False,
                    active_dot={"r": 6},
                ),
                rx.recharts.line(
                    data_key="Engineering",
                    stroke="#f97316",
                    stroke_width=2,
                    dot=False,
                    active_dot={"r": 6},
                ),
                rx.recharts.line(
                    data_key="Office Renovation",
                    stroke="#14b8a6",
                    stroke_width=2,
                    dot=False,
                    active_dot={"r": 6},
                ),
                rx.recharts.line(
                    data_key="Sales",
                    stroke="#ec4899",
                    stroke_width=2,
                    dot=False,
                    active_dot={"r": 6},
                ),
                rx.recharts.line(
                    data_key="HR",
                    stroke="#8b5cf6",
                    stroke_width=2,
                    dot=False,
                    active_dot={"r": 6},
                ),
                rx.recharts.line(
                    data_key="Website Redesign",
                    stroke="#3b82f6",
                    stroke_width=2,
                    dot=False,
                    active_dot={"r": 6},
                ),
                data=BudgetState.monthly_trends,
                height=300,
                width="100%",
            ),
            custom_legend(),
            class_name="w-full h-[330px]",
        ),
        class_name="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm",
    )


def distribution_chart() -> rx.Component:
    """"""

    return rx.el.div(
        rx.el.h3(
            "Expense Distribution",
            class_name="text-lg font-bold text-gray-900 dark:text-gray-100 mb-6",
        ),
        rx.el.div(
            rx.recharts.pie_chart(
                rx.recharts.pie(
                    data=BudgetState.category_distribution,
                    data_key="value",
                    name_key="name",
                    cx="50%",
                    cy="50%",
                    inner_radius=60,
                    outer_radius=80,
                    fill="#8884d8",
                    label=True,
                    stroke="#fff",
                    stroke_width=2,
                ),
                rx.recharts.tooltip(
                    content_style={
                        "backgroundColor": "#fff",
                        "borderRadius": "8px",
                        "border": "none",
                        "boxShadow": "0 4px 6px -1px rgb(0 0 0 / 0.1)",
                    }
                ),
                height=300,
                width="100%",
            ),
            class_name="w-full h-[300px] flex items-center justify-center",
        ),
        class_name="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm",
    )


def create_gradient(color: str, id: str) -> rx.Component:
    """"""

    return rx.el.svg.defs(
        rx.el.svg.linear_gradient(
            rx.el.svg.stop(stop_color=color, offset="5%", stop_opacity=0.5),
            rx.el.svg.stop(stop_color=color, offset="95%", stop_opacity=0),
            x1=0,
            x2=0,
            y1=0,
            y2=1,
            id=id,
        )
    )


def forecast_chart() -> rx.Component:
    """"""

    return rx.el.div(
        rx.el.h3(
            "Spending Projection",
            class_name="text-lg font-bold text-gray-900 dark:text-gray-100 mb-6",
        ),
        rx.el.div(
            rx.recharts.area_chart(
                rx.recharts.cartesian_grid(
                    stroke_dasharray="3 3", vertical=False, class_name="stroke-gray-200"
                ),
                create_gradient("#6366f1", "colorIndigo"),
                create_gradient("#9ca3af", "colorGray"),
                rx.recharts.x_axis(
                    data_key="month",
                    axis_line=False,
                    tick_line=False,
                    tick={"fontSize": 12, "fill": "#6b7280"},
                    dy=10,
                ),
                rx.recharts.y_axis(
                    axis_line=False,
                    tick_line=False,
                    tick={"fontSize": 12, "fill": "#6b7280"},
                ),
                rx.recharts.tooltip(
                    content_style={
                        "backgroundColor": "#fff",
                        "borderRadius": "8px",
                        "border": "none",
                        "boxShadow": "0 4px 6px -1px rgb(0 0 0 / 0.1)",
                    }
                ),
                rx.recharts.area(
                    data_key="actual",
                    name="Actual Spend",
                    stroke="#6366f1",
                    fill="url(#colorIndigo)",
                    stroke_width=3,
                    type_="monotone",
                ),
                rx.recharts.area(
                    data_key="projected",
                    name="Projected Spend",
                    stroke="#9ca3af",
                    fill="url(#colorGray)",
                    stroke_dasharray="5 5",
                    stroke_width=2,
                    type_="monotone",
                ),
                data=BudgetState.spending_forecast,
                height=300,
                width="100%",
                margin={"top": 10, "right": 10, "left": 0, "bottom": 0},
            ),
            class_name="w-full h-[320px]",
        ),
        class_name="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm h-full",
    )


def department_comparison_chart() -> rx.Component:
    """"""

    return rx.el.div(
        rx.el.h3(
            "Department Budget vs. Spend",
            class_name="text-lg font-bold text-gray-900 dark:text-gray-100 mb-6",
        ),
        rx.el.div(
            rx.recharts.bar_chart(
                rx.recharts.cartesian_grid(
                    stroke_dasharray="3 3",
                    horizontal=False,
                    class_name="stroke-gray-200",
                ),
                rx.recharts.x_axis(
                    type_="number",
                    axis_line=False,
                    tick_line=False,
                    tick={"fontSize": 12, "fill": "#6b7280"},
                ),
                rx.recharts.y_axis(
                    data_key="name",
                    type_="category",
                    width=100,
                    axis_line=False,
                    tick_line=False,
                    tick={"fontSize": 12, "fill": "#6b7280"},
                ),
                rx.recharts.tooltip(
                    content_style={
                        "backgroundColor": "#fff",
                        "borderRadius": "8px",
                        "border": "none",
                        "boxShadow": "0 4px 6px -1px rgb(0 0 0 / 0.1)",
                    }
                ),
                rx.recharts.bar(
                    data_key="Budget", fill="#e5e7eb", radius=[0, 4, 4, 0], bar_size=12
                ),
                rx.recharts.bar(
                    data_key="Spent", fill="#6366f1", radius=[0, 4, 4, 0], bar_size=12
                ),
                data=BudgetState.department_comparison_data,
                layout="vertical",
                height=320,
                width="100%",
            ),
            rx.el.div(
                legend_item("Budget", "#e5e7eb"),
                legend_item("Spent", "#6366f1"),
                class_name="flex flex-wrap items-center gap-4 justify-center mt-4",
            ),
            class_name="w-full",
        ),
        class_name="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm h-full",
    )


def top_spenders_widget() -> rx.Component:
    """"""
    return rx.el.div(
        rx.el.h3(
            "Top Spenders",
            class_name="text-lg font-bold text-gray-900 dark:text-gray-100 mb-4",
        ),
        class_name="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm h-full",
    )


def comparison_table() -> rx.Component:
    """"""
    return rx.el.div(
        rx.el.h3(
            "Budget vs. Actuals",
            class_name="text-lg font-bold text-gray-900 dark:text-gray-100 mb-6",
        ),
        rx.el.div(
            rx.el.table(
                rx.el.thead(
                    rx.el.tr(
                        rx.el.th(
                            "Category",
                            class_name="px-6 py-3 text-left text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider",
                        ),
                        rx.el.th(
                            "Allocated",
                            class_name="px-6 py-3 text-right text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider",
                        ),
                        rx.el.th(
                            "Actual Spent",
                            class_name="px-6 py-3 text-right text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider",
                        ),
                        rx.el.th(
                            "Variance",
                            class_name="px-6 py-3 text-right text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider",
                        ),
                        rx.el.th(
                            "Utilization",
                            class_name="px-6 py-3 text-right text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider",
                        ),
                        class_name="bg-gray-50 border-b border-gray-200",
                    )
                ),
                rx.el.tbody(
                    rx.foreach(
                        BudgetState.budget_stats,
                        lambda b: rx.el.tr(
                            rx.el.td(
                                rx.el.div(
                                    b["name"],
                                    class_name="font-medium text-gray-900 dark:text-gray-100",
                                ),
                                class_name="px-6 py-4 whitespace-nowrap text-sm",
                            ),
                            rx.el.td(
                                f"${b['allocated_amount']:,.2f}",
                                class_name="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-400 text-right font-medium",
                            ),
                            rx.el.td(
                                f"${b['spent']:,.2f}",
                                class_name="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-400 text-right font-medium",
                            ),
                            rx.el.td(
                                rx.el.span(
                                    rx.cond(
                                        b["remaining"] >= 0,
                                        f"+${b['remaining']:,.2f}",
                                        f"${b['remaining']:,.2f}",
                                    ),
                                    class_name=rx.cond(
                                        b["remaining"] >= 0,
                                        "text-emerald-600 font-bold",
                                        "text-red-600 font-bold",
                                    ),
                                ),
                                class_name="px-6 py-4 whitespace-nowrap text-sm text-right",
                            ),
                            rx.el.td(
                                rx.el.div(
                                    rx.el.span(
                                        f"{b['utilization']}%",
                                        class_name=f"inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium {b['health_bg']} {b['health_color']}",
                                    ),
                                    class_name="flex justify-end",
                                ),
                                class_name="px-6 py-4 whitespace-nowrap text-right",
                            ),
                            class_name="border-b border-gray-100 hover:bg-gray-50/50 transition-colors",
                        ),
                    ),
                    class_name="bg-white divide-y divide-gray-100",
                ),
                rx.el.tfoot(
                    rx.el.tr(
                        rx.el.td(
                            "Total",
                            class_name="px-6 py-4 whitespace-nowrap text-sm font-bold text-gray-900 dark:text-gray-100",
                        ),
                        rx.el.td(
                            f"${BudgetState.total_budget:,.2f}",
                            class_name="px-6 py-4 whitespace-nowrap text-sm font-bold text-gray-900 dark:text-gray-100 text-right",
                        ),
                        rx.el.td(
                            f"${BudgetState.total_spent:,.2f}",
                            class_name="px-6 py-4 whitespace-nowrap text-sm font-bold text-gray-900 dark:text-gray-100 text-right",
                        ),
                        rx.el.td(
                            rx.el.span(
                                rx.cond(
                                    BudgetState.remaining_budget >= 0,
                                    f"+${BudgetState.remaining_budget:,.2f}",
                                    f"${BudgetState.remaining_budget:,.2f}",
                                ),
                                class_name=rx.cond(
                                    BudgetState.remaining_budget >= 0,
                                    "text-emerald-600 font-bold",
                                    "text-red-600 font-bold",
                                ),
                            ),
                            class_name="px-6 py-4 whitespace-nowrap text-sm text-right",
                        ),
                        rx.el.td(
                            rx.el.div(
                                rx.el.span(
                                    f"{BudgetState.utilization_percentage}%",
                                    class_name=f"inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold {BudgetState.budget_health_bg} {BudgetState.budget_health_color}",
                                ),
                                class_name="flex justify-end",
                            ),
                            class_name="px-6 py-4 whitespace-nowrap text-right",
                        ),
                        class_name="bg-gray-50/50 border-t border-gray-200",
                    )
                ),
                class_name="min-w-full divide-y divide-gray-200",
            ),
            class_name="overflow-x-auto rounded-xl border border-gray-200",
        ),
        class_name="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm",
    )


def reports_page() -> rx.Component:
    """"""

    return rx.el.div(
        rx.el.div(
            class_name="fixed inset-0 bg-gradient-to-br from-indigo-50/50 via-purple-50/30 to-white -z-10"
        ),
        sidebar(),
        rx.el.div(
            header(),
            rx.el.main(
                rx.el.div(
                    rx.el.div(
                        rx.el.div(
                            rx.el.h2(
                                "Reports & Analytics",
                                class_name="text-3xl font-bold text-gray-900 dark:text-gray-100 tracking-tight",
                            ),
                            rx.el.p(
                                "Deep dive into your financial performance.",
                                class_name="text-gray-500 dark:text-gray-400 mt-2 text-lg",
                            ),
                        ),
                        rx.el.select(
                            rx.el.option("Year to Date", value="Year to Date"),
                            rx.el.option("Last 6 Months", value="Last 6 Months"),
                            rx.el.option("Last 3 Months", value="Last 3 Months"),
                            rx.el.option("All Time", value="All Time"),
                            value=BudgetState.report_date_range,
                            on_change=BudgetState.set_report_date_range,
                            class_name="px-4 py-2.5 rounded-xl border border-gray-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm font-medium bg-white/50 backdrop-blur-sm",
                        ),
                        class_name="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-10 animate-in fade-in slide-in-from-bottom-4 duration-500",
                    ),
                    rx.el.div(
                        summary_stat(
                            "Total Spent YTD",
                            f"${BudgetState.total_spent:,.2f}",
                            "+12% vs last year",
                            icon="dollar-sign",
                            icon_color="blue",
                        ),
                        summary_stat(
                            "Remaining Budget",
                            f"${BudgetState.remaining_budget:,.2f}",
                            f"{100 - BudgetState.utilization_percentage}% of total",
                            icon="wallet",
                            icon_color="emerald",
                        ),
                        summary_stat(
                            "Top Category",
                            BudgetState.top_spending_category,
                            "Most active sector",
                            icon="tag",
                            icon_color="purple",
                        ),
                        summary_stat(
                            "Active Budgets",
                            f"{BudgetState.budgets.length()}",
                            "Across all departments",
                            icon="layers",
                            icon_color="orange",
                        ),
                        class_name="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8 animate-in fade-in slide-in-from-bottom-6 duration-700",
                    ),
                    rx.el.div(
                        rx.el.div(forecast_chart(), class_name="lg:col-span-2"),
                        rx.el.div(top_spenders_widget(), class_name="lg:col-span-1"),
                        class_name="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8 animate-in fade-in slide-in-from-bottom-7 duration-700",
                    ),
                    rx.el.div(
                        rx.el.div(trend_chart(), class_name="lg:col-span-2"),
                        rx.el.div(distribution_chart(), class_name="lg:col-span-1"),
                        class_name="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8 animate-in fade-in slide-in-from-bottom-8 duration-700",
                    ),
                    rx.el.div(
                        rx.el.div(
                            department_comparison_chart(), class_name="lg:col-span-2"
                        ),
                        rx.el.div(
                            rx.el.div(
                                rx.el.h3(
                                    "Export Reports",
                                    class_name="text-lg font-bold text-gray-900 dark:text-gray-100 mb-4",
                                ),
                                rx.el.p(
                                    "Download detailed financial reports for your team.",
                                    class_name="text-sm text-gray-500 dark:text-gray-400 mb-6",
                                ),
                                rx.el.button(
                                    rx.icon("file-down", size=20, class_name="mr-2"),
                                    "Export as PDF",
                                    on_click=BudgetState.export_report_pdf,
                                    class_name="w-full flex items-center justify-center px-4 py-3 bg-indigo-600 hover:bg-indigo-700 text-white font-medium rounded-xl transition-colors mb-3 shadow-sm",
                                ),
                                rx.el.button(
                                    rx.icon("table", size=20, class_name="mr-2"),
                                    "Export as CSV",
                                    on_click=BudgetState.export_selected_expenses,
                                    class_name="w-full flex items-center justify-center px-4 py-3 bg-white border border-gray-200 hover:bg-gray-50 text-gray-700 font-medium rounded-xl transition-colors shadow-sm",
                                ),
                                class_name="bg-gradient-to-br from-indigo-50/50 to-purple-50/50 p-6 rounded-2xl border border-indigo-100 shadow-sm h-full flex flex-col justify-center",
                            ),
                            class_name="lg:col-span-1",
                        ),
                        class_name="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8 animate-in fade-in slide-in-from-bottom-9 duration-700",
                    ),
                    rx.el.div(
                        comparison_table(),
                        class_name="animate-in fade-in slide-in-from-bottom-10 duration-700",
                    ),
                    class_name="max-w-7xl mx-auto relative z-10",
                ),
                class_name="flex-1 p-6 md:p-8 pt-8 md:pt-10 overflow-y-auto scroll-smooth",
            ),
            class_name="flex-1 flex flex-col h-screen overflow-hidden",
        ),
        class_name="flex h-screen bg-gray-50 font-['Inter']",
    )
