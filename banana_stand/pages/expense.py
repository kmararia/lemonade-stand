"""
Expenses page layout configurations
"""

# from datetime import datetime

# import dash
# import polars as pl
# from dash import Input
# from dash import Output
# from dash import dcc
# from dash import html

# from lemonade_stand.data_store import USER_DATA

# # Define module variables
# CATEGORY_LIST = USER_DATA.expenses["category"].unique().sort().to_list()
# MIN_DATE = str(USER_DATA.expenses["date"].min())
# MAX_DATE = str(USER_DATA.expenses["date"].max())


# # Set up page layout

# svg_arrow = """
# <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
#   <path d="M12 4l1.41 1.41L7.83 11H20v2H7.83l5.58 5.59L12 20l-8-8z"/>
# </svg>
# """

# layout = html.Div(
#     [
#         html.Button(
#             [
#                 html.Span("Click Me", className="text"),
#                 html.Span(className="circle"),
#                 html.Span(svg_arrow, className="arr-1", dangerously_allow_html=True),
#                 html.Span(svg_arrow, className="arr-2", dangerously_allow_html=True),
#             ],
#             className="animated-button",
#         ),
#     ]
# )

# # Register page
# dash.register_page(
#     __name__, path="/expenses", name="Expenses", title="Expenses - Banana Stand"
# )
