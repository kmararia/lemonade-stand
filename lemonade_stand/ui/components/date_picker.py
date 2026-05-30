""""""

import reflex as rx

from lemonade_stand.ui.states.ui_state import DateState


def date_picker() -> rx.Component:
    """
    A date picker component that allows users to select a year and month.
    """

    return rx.popover.root(
        rx.popover.trigger(
            rx.button(
                DateState.button_display_text,
                rx.icon("calendar", size=16, class_name="ml-2"),
                variant="soft",
                radius="large",
                color_scheme="mint",
                class_name="cursor-pointer",
            )
        ),
        rx.popover.content(
            rx.flex(
                # Year Dropdown
                rx.select(
                    DateState.available_years,
                    value=DateState.selected_year,
                    on_change=DateState.set_year,
                    placeholder="All Years",
                    color_scheme="mint",
                    variant="ghost",
                    size="1",
                ),
                # Month Dropdown
                rx.select(
                    DateState.available_months,
                    value=DateState.selected_month,
                    on_change=DateState.set_month,
                    placeholder="All Months",
                    color_scheme="mint",
                    variant="ghost",
                    size="1",
                ),
                direction="row-reverse",
                justify="between",
                spacing="4",
            ),
            align="end",
            side="bottom",
            side_offset=2,
            width="100%",
            height="auto",
            class_name="p-3",
        ),
    )
