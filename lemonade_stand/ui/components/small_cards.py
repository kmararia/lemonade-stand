""""""

import typing
from decimal import Decimal

import reflex as rx


def summary_stats_card(
    label: str,
    value: str,
    subtext: str | tuple[typing.Any, ...] = "",
    icon: str = "activity",
    icon_color: str = "indigo",
    progress: rx.Var[int | float | Decimal] | None = None,
) -> rx.Component:
    """"""

    if isinstance(subtext, str):
        subtext_items = (subtext, "trending-up", "emerald")
    else:
        subtext_items = (
            subtext[0],
            rx.cond(len(subtext) > 1, subtext[1], "trending-up"),
            rx.cond(len(subtext) > 2, subtext[2], "emerald"),
        )

    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.p(
                    label,
                    class_name="text-xs font-semibold text-[var(--text-muted)] uppercase tracking-wider mb-1",
                ),
                rx.el.h3(
                    value,
                    class_name="text-xl font-bold text-[var(--text-main)] tracking-tight",
                ),
                class_name="flex flex-col",
            ),
            rx.el.div(
                rx.icon(
                    icon,
                    size=20,
                    class_name=f"text-{icon_color}-200 dark:text-{icon_color}-500 transition-colors",
                ),
                class_name=f"p-2.5 rounded-xl bg-{icon_color}-600/10 group-hover:scale-110 transition-transform duration-300 shadow-sm",
            ),
            class_name="flex justify-between items-start mb-4",
        ),
        rx.cond(
            progress is not None,
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        class_name=f"h-2 rounded-full bg-gradient-to-r from-{icon_color}-500 to-{icon_color}-400 transition-all duration-1000 ease-out",
                        style={"width": f"{progress}%"},
                    ),
                    class_name="w-full h-2 bg-[var(--bg-card)] rounded-full overflow-hidden",
                ),
                rx.el.span(
                    subtext_items[0],
                    class_name=f"text-xs font-medium text-{icon_color}-600 dark:text-{icon_color}-400 mt-2",
                ),
                class_name="w-full",
            ),
            rx.cond(
                subtext != "",
                rx.el.div(
                    rx.icon(
                        subtext_items[1],
                        size=14,
                        class_name=rx.match(
                            subtext_items[2],
                            ("red", "text-[var(--critical-text)] mr-1"),
                            ("yellow", "text-[var(--warning-text)] mr-1"),
                            ("emerald", "text-[var(--healthy-text)] mr-1"),
                            ("green", "text-green-500 mr-1"),
                            f"text-{subtext_items[2]}-500 mr-1",
                        ),
                    ),
                    rx.el.span(
                        subtext_items[0],
                        class_name="text-xs font-medium text-[var(--text-muted)]",
                    ),
                    class_name="flex items-center",
                ),
                rx.el.span(class_name="hidden"),
            ),
        ),
        class_name="""
            group bg-[var(--bg-card)] backdrop-blur-sm p-6 rounded-2xl
            border border-[var(--border-main)]
            shadow-[0_8px_30px_rgb(0,0,0,0.04)] hover:shadow-[0_8px_30px_rgb(0,0,0,0.08)]
            transition-all duration-300 hover:-translate-y-1
        """,
    )
