""" """

import typing

import reflex as rx


def modal_input_field(
    label: str,
    value: rx.Var,
    on_change: typing.Any,
    field_name: str,
    config: dict[str, typing.Any] | None = None,
) -> rx.Component:
    """A standardized, reusable input field for all modals."""

    input_class = """
        w-full text-sm font-medium text-[var(--text-main)]
        bg-[var(--bg-card)] border border-[var(--border-main)]
        rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 py-2 px-3
    """

    config = {} if config is None else config

    def _partial_on_change(new_val):
        return on_change(field_name, new_val)

    # Dynamically choose between input or textarea
    input_component = rx.cond(
        config.get("is_textarea", False),
        rx.text_area(value=value, on_change=_partial_on_change, class_name=input_class),
        rx.cond(
            config.get("select_options", None) is not None,
            rx.select(
                config.get("select_options", []),
                default_value=value,
                on_change=_partial_on_change,
                class_name=input_class,
            ),
            rx.input(
                value=value,
                on_change=_partial_on_change,
                type=config.get("input_type", "text"),
                class_name=input_class,
            ),
        ),
    )

    return rx.el.div(
        rx.el.label(
            label,
            class_name="block text-xs font-semibold text-[var(--text-muted)] mb-1.5 uppercase tracking-wider",
        ),
        input_component,
        class_name="col-span-2" if config.get("col_span_2", False) else "col-span-1",
    )


def generic_edit_modal(
    *form_fields: rx.Component,
    title: str,
    description: str,
    is_open: bool,
    on_open_change: typing.Any,
    on_save: typing.Any,
) -> rx.Component:
    """The master modal shell that handles layout, state, and actions for ANY form."""

    return rx.dialog.root(
        rx.dialog.content(
            # Modal Header
            rx.el.div(
                rx.dialog.title(
                    title,
                    class_name="text-lg font-bold text-[var(--text-main)]",
                ),
                rx.dialog.description(
                    description,
                    class_name="text-sm text-[var(--text-muted)] mt-1",
                ),
                class_name="mt-4 mb-6",
            ),
            # Modal Form Fields
            rx.el.div(
                *form_fields,
                class_name="grid grid-cols-2 gap-4 mb-8",
            ),
            # Modal Action Buttons
            rx.el.div(
                rx.dialog.close(
                    rx.el.button(
                        "Cancel",
                        class_name="px-4 py-2 text-sm font-medium text-[var(--text-muted)] hover:bg-[var(--critical-bg)] rounded-lg transition-colors",
                    ),
                ),
                rx.dialog.close(
                    rx.el.button(
                        "Save Changes",
                        on_click=on_save,
                        class_name="px-4 py-2 text-sm font-medium text-white bg-[var(--healthy-bg)] hover:bg-[var(--warning-bg)] rounded-lg shadow-sm transition-colors",
                    ),
                ),
                class_name="flex justify-end gap-3",
            ),
            class_name="max-w-md w-full bg-[var(--bg-card)] backdrop-blur-2xl p-6 rounded-2xl border border-[var(--border-main)] shadow-2xl outline-none",
        ),
        open=is_open,
        on_open_change=on_open_change,
    )
