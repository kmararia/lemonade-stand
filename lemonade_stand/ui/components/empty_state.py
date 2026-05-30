""""""

import reflex as rx


def empty_state(
    icon: str,
    title: str,
    description: str,
    action_label: str | None = None,
    on_click: rx.event.EventType = None,
) -> rx.Component:
    """"""

    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.icon(icon, size=48, class_name="text-indigo-200 mb-4 mx-auto"),
                class_name="w-24 h-24 bg-indigo-50 dark:bg-cyan-900/30 rounded-full flex items-center justify-center mx-auto mb-6",
            ),
            rx.el.h3(
                title,
                class_name="text-xl font-bold text-gray-900 dark:text-gray-100 mb-2",
            ),
            rx.el.p(
                description,
                class_name="text-gray-500 dark:text-gray-400 mb-8 max-w-md mx-auto",
            ),
            rx.cond(
                action_label is not None,
                rx.el.button(
                    rx.icon("plus", size=18, class_name="mr-2"),
                    action_label,
                    on_click=on_click,
                    class_name="inline-flex items-center px-5 py-2.5 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 transition-all shadow-md hover:shadow-lg font-medium text-sm hover:-translate-y-0.5",
                ),
            ),
            class_name="text-center py-12 px-4",
        ),
        class_name="bg-white/40 backdrop-blur-sm rounded-3xl border-2 border-dashed border-gray-200/60 flex flex-col items-center justify-center min-h-[400px] w-full animate-in fade-in zoom-in duration-500",
    )
