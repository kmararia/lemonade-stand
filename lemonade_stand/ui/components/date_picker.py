""""""

import reflex as rx

from lemonade_stand.ui.states.data_state import DataState


def date_picker() -> rx.Component:
    """
    A date picker component that allows users to select a year and month.
    """

    return rx.popover.root(
        rx.popover.trigger(
            rx.button(
                rx.icon("calendar_days", size=16, class_name="ml-2"),
                DataState.date_selection_text,
                variant="soft",
                radius="large",
                color_scheme="mint",
                class_name="cursor-pointer text-[var(--selected-color)] hover:text-[var(--text-main)] transition-colors",
            ),
            class_name="pr-5 pl-0 flex justify-left",
        ),
        rx.popover.content(
            rx.flex(
                # Year Dropdown
                rx.select(
                    DataState.available_years.keys(),
                    value=DataState.selected_year,
                    on_change=DataState.set_year,
                    placeholder="All Years",
                    color_scheme="mint",
                    variant="ghost",
                    size="1",
                ),
                # Month Dropdown
                rx.select.root(
                    rx.select.trigger(
                        placeholder="All Months",
                        color_scheme="mint",
                        variant="ghost",
                    ),
                    rx.select.content(
                        rx.select.group(
                            rx.foreach(
                                DataState.available_months,
                                lambda month: rx.select.item(
                                    month[0], value=month[0], disabled=month[1]
                                ),
                            ),
                        ),
                        color_scheme="mint",
                        variant="solid",
                    ),
                    value=DataState.selected_month,
                    on_change=DataState.set_month,
                    size="1",
                ),
                direction="row-reverse",
                justify="between",
                spacing="6",
            ),
            align="end",
            side="bottom",
            side_offset=2,
            width="100%",
            height="auto",
            class_name="p-3",
        ),
    )
