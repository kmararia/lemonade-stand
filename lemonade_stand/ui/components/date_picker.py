""""""

import reflex as rx

from lemonade_stand.ui.states.home_state import HomeState


def date_picker() -> rx.Component:
    """
    A date picker component that allows users to select a year and month.
    """

    return rx.popover.root(
        rx.popover.trigger(
            rx.button(
                HomeState.date_selection_text,
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
                    HomeState.available_years,
                    value=HomeState.selected_year,
                    on_change=HomeState.set_year,
                    placeholder="All Years",
                    color_scheme="mint",
                    variant="ghost",
                    size="1",
                ),
                # Month Dropdown
                rx.select(
                    HomeState.available_months,
                    value=HomeState.selected_month,
                    on_change=HomeState.set_month,
                    placeholder="All Months",
                    color_scheme="mint",
                    variant="ghost",
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
