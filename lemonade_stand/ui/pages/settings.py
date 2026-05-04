""""""

import reflex as rx

from lemonade_stand.ui.components.header import header
from lemonade_stand.ui.components.sidebar import sidebar
from lemonade_stand.ui.states.budget_state import BudgetState
from lemonade_stand.ui.states.settings_state import SettingsState


def section_header(title: str, description: str) -> rx.Component:
    """"""

    return rx.el.div(
        rx.el.h3(title, class_name="text-lg font-bold text-gray-900"),
        rx.el.p(description, class_name="text-sm text-gray-500 mt-1"),
        class_name="mb-6",
    )


def category_list_item(name: str, on_delete: rx.event.EventType) -> rx.Component:
    """"""

    return rx.el.div(
        rx.el.span(name, class_name="text-sm text-gray-700 font-medium"),
        rx.el.button(
            rx.icon("x", size=14, class_name="text-gray-400"),
            on_click=on_delete,
            class_name="p-1 hover:bg-red-50 hover:text-red-600 rounded transition-colors",
        ),
        class_name="flex items-center justify-between p-3 bg-gray-50 rounded-lg",
    )


def category_settings() -> rx.Component:
    """"""

    return rx.el.div(
        section_header(
            "Categories & Projects", "Manage the structure of your budget tracking."
        ),
        rx.el.div(
            rx.el.div(
                rx.el.h4(
                    "Departments",
                    class_name="text-sm font-semibold text-gray-900 mb-3 uppercase tracking-wider",
                ),
                rx.el.div(
                    rx.foreach(
                        BudgetState.departments,
                        lambda d: category_list_item(
                            d, lambda: BudgetState.remove_department(d)
                        ),
                    ),
                    class_name="space-y-2 mb-4",
                ),
                rx.el.div(
                    rx.el.input(
                        placeholder="New Department",
                        on_change=SettingsState.set_new_department_input,
                        class_name="flex-1 min-w-0 rounded-lg border-gray-200 text-sm focus:ring-indigo-500 focus:border-indigo-500 px-3 py-2 border",
                        default_value=SettingsState.new_department_input,
                    ),
                    rx.el.button(
                        "Add",
                        on_click=SettingsState.add_department,
                        class_name="ml-2 px-3 py-2 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700",
                    ),
                    class_name="flex",
                ),
                class_name="bg-white p-5 rounded-xl border border-gray-200",
            ),
            rx.el.div(
                rx.el.h4(
                    "Projects",
                    class_name="text-sm font-semibold text-gray-900 mb-3 uppercase tracking-wider",
                ),
                rx.el.div(
                    rx.foreach(
                        BudgetState.projects,
                        lambda p: category_list_item(
                            p, lambda: BudgetState.remove_project(p)
                        ),
                    ),
                    class_name="space-y-2 mb-4",
                ),
                rx.el.div(
                    rx.el.input(
                        placeholder="New Project",
                        on_change=SettingsState.set_new_project_input,
                        class_name="flex-1 min-w-0 rounded-lg border-gray-200 text-sm focus:ring-indigo-500 focus:border-indigo-500 px-3 py-2 border",
                        default_value=SettingsState.new_project_input,
                    ),
                    rx.el.button(
                        "Add",
                        on_click=SettingsState.add_project,
                        class_name="ml-2 px-3 py-2 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700",
                    ),
                    class_name="flex",
                ),
                class_name="bg-white p-5 rounded-xl border border-gray-200",
            ),
            class_name="grid grid-cols-1 md:grid-cols-2 gap-6",
        ),
        class_name="mb-10",
    )


def threshold_settings() -> rx.Component:
    """"""

    return rx.el.div(
        section_header(
            "Budget Alerts",
            "Configure when you want to be warned about spending limits.",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.label(
                        "Warning Threshold",
                        class_name="text-sm font-medium text-gray-900",
                    ),
                    rx.el.span(
                        f"{BudgetState.warning_threshold}%",
                        class_name="text-sm font-bold text-orange-500",
                    ),
                    class_name="flex justify-between mb-2",
                ),
                rx.el.input(
                    type="range",
                    min="0",
                    max="100",
                    default_value=BudgetState.warning_threshold,
                    key=f"warning-threshold-{BudgetState.warning_threshold}",
                    on_change=BudgetState.set_warning_threshold.throttle(500),
                    class_name="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-orange-500",
                ),
                rx.el.p(
                    "Budgets will turn orange when utilization exceeds this value.",
                    class_name="text-xs text-gray-500 mt-2",
                ),
                class_name="bg-white p-5 rounded-xl border border-gray-200",
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.label(
                        "Critical Threshold",
                        class_name="text-sm font-medium text-gray-900",
                    ),
                    rx.el.span(
                        f"{BudgetState.critical_threshold}%",
                        class_name="text-sm font-bold text-red-600",
                    ),
                    class_name="flex justify-between mb-2",
                ),
                rx.el.input(
                    type="range",
                    min="0",
                    max="100",
                    default_value=BudgetState.critical_threshold,
                    key=f"critical-threshold-{BudgetState.critical_threshold}",
                    on_change=BudgetState.set_critical_threshold.throttle(500),
                    class_name="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-red-600",
                ),
                rx.el.p(
                    "Budgets will turn red when utilization exceeds this value.",
                    class_name="text-xs text-gray-500 mt-2",
                ),
                class_name="bg-white p-5 rounded-xl border border-gray-200",
            ),
            class_name="grid grid-cols-1 md:grid-cols-2 gap-6",
        ),
        class_name="mb-10",
    )


def regional_settings() -> rx.Component:
    """"""

    return rx.el.div(
        section_header(
            "Regional Settings", "Set your preferred currency and date formats."
        ),
        rx.el.div(
            rx.el.div(
                rx.el.label(
                    "Currency",
                    class_name="block text-sm font-medium text-gray-700 mb-1",
                ),
                rx.el.select(
                    rx.el.option("USD ($)", value="USD ($)"),
                    rx.el.option("EUR (€)", value="EUR (€)"),
                    rx.el.option("GBP (£)", value="GBP (£)"),
                    rx.el.option("JPY (¥)", value="JPY (¥)"),
                    rx.el.option("CAD ($)", value="CAD ($)"),
                    value=SettingsState.currency_format,
                    on_change=SettingsState.set_currency_format,
                    class_name="w-full rounded-lg border-gray-200 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 px-4 py-2 border bg-gray-50",
                ),
                class_name="col-span-1",
            ),
            rx.el.div(
                rx.el.label(
                    "Date Format",
                    class_name="block text-sm font-medium text-gray-700 mb-1",
                ),
                rx.el.select(
                    rx.el.option("MM/DD/YYYY", value="MM/DD/YYYY"),
                    rx.el.option("DD/MM/YYYY", value="DD/MM/YYYY"),
                    rx.el.option("YYYY-MM-DD", value="YYYY-MM-DD"),
                    value=SettingsState.date_format,
                    on_change=SettingsState.set_date_format,
                    class_name="w-full rounded-lg border-gray-200 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 px-4 py-2 border bg-gray-50",
                ),
                class_name="col-span-1",
            ),
            class_name="grid grid-cols-1 md:grid-cols-2 gap-6 bg-white p-5 rounded-xl border border-gray-200",
        ),
        class_name="mb-10",
    )


def notification_toggle(
    label: str, checked: bool, on_change: rx.event.EventType
) -> rx.Component:
    """"""

    return rx.el.div(
        rx.el.div(rx.el.h4(label, class_name="text-sm font-medium text-gray-900")),
        rx.el.label(
            rx.el.input(
                type="checkbox",
                default_checked=checked,
                on_change=on_change,
                class_name="sr-only peer",
            ),
            rx.el.div(
                class_name="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-indigo-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-indigo-600"
            ),
            class_name="relative inline-flex items-center cursor-pointer",
        ),
        class_name="flex items-center justify-between py-4 border-b border-gray-100 last:border-0",
    )


def general_settings() -> rx.Component:
    """"""

    return rx.el.div(
        section_header(
            "General Preferences", "Customize your experience and notifications."
        ),
        rx.el.div(
            rx.el.div(
                rx.el.h4(
                    "Notifications",
                    class_name="text-sm font-semibold text-gray-900 mb-4 uppercase tracking-wider",
                ),
                notification_toggle(
                    "Email Alerts",
                    SettingsState.notifications_email,
                    SettingsState.toggle_notifications_email,
                ),
                notification_toggle(
                    "Dashboard Alerts",
                    SettingsState.notifications_dashboard,
                    SettingsState.toggle_notifications_dashboard,
                ),
                notification_toggle(
                    "Weekly Summary",
                    SettingsState.notifications_weekly,
                    SettingsState.toggle_notifications_weekly,
                ),
                class_name="bg-white p-5 rounded-xl border border-gray-200 mb-6",
            ),
            rx.el.div(
                rx.el.h4(
                    "Data Management",
                    class_name="text-sm font-semibold text-gray-900 mb-4 uppercase tracking-wider",
                ),
                rx.el.div(
                    rx.el.div(
                        rx.el.p(
                            "Export Data",
                            class_name="text-sm font-medium text-gray-900",
                        ),
                        rx.el.p(
                            "Download a full report of your budget history.",
                            class_name="text-xs text-gray-500",
                        ),
                    ),
                    rx.el.button(
                        rx.icon("download", size=16, class_name="mr-2"),
                        "Export CSV",
                        on_click=SettingsState.export_data,
                        class_name="flex items-center px-3 py-2 bg-white border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50",
                    ),
                    class_name="flex items-center justify-between p-4 bg-gray-50 rounded-lg",
                ),
                class_name="bg-white p-5 rounded-xl border border-gray-200",
            ),
            class_name="grid grid-cols-1 md:grid-cols-2 gap-6",
        ),
        class_name="mb-6",
    )


def settings_page() -> rx.Component:
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
                        rx.el.h2(
                            "Settings",
                            class_name="text-3xl font-bold text-gray-900 tracking-tight",
                        ),
                        rx.el.p(
                            "Manage your preferences and configurations.",
                            class_name="text-gray-500 mt-2 text-lg",
                        ),
                        class_name="mb-10 animate-in fade-in slide-in-from-bottom-4 duration-500",
                    ),
                    rx.el.div(
                        rx.el.div(
                            category_settings(),
                            class_name="animate-in fade-in slide-in-from-bottom-6 duration-700",
                        ),
                        rx.el.div(
                            threshold_settings(),
                            class_name="animate-in fade-in slide-in-from-bottom-8 duration-700",
                        ),
                        rx.el.div(
                            regional_settings(),
                            class_name="animate-in fade-in slide-in-from-bottom-9 duration-700",
                        ),
                        rx.el.div(
                            general_settings(),
                            class_name="animate-in fade-in slide-in-from-bottom-10 duration-700",
                        ),
                        rx.el.div(
                            rx.el.button(
                                "Save Changes",
                                on_click=SettingsState.save_settings,
                                class_name="px-8 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-semibold rounded-xl hover:shadow-lg hover:shadow-indigo-200 shadow-sm transition-all transform hover:scale-105 active:scale-95",
                            ),
                            class_name="flex justify-end pt-8 border-t border-gray-200/50 mt-8 animate-in fade-in slide-in-from-bottom-12 duration-700",
                        ),
                        class_name="bg-white/70 backdrop-blur-xl rounded-2xl p-8 border border-white/50 shadow-[0_8px_30px_rgb(0,0,0,0.04)]",
                    ),
                    class_name="max-w-5xl mx-auto relative z-10",
                ),
                class_name="flex-1 p-6 md:p-8 overflow-y-auto scroll-smooth",
            ),
            class_name="flex-1 flex flex-col h-screen overflow-hidden",
        ),
        class_name="flex h-screen bg-gray-50 font-['Inter']",
    )
