"""
wrangle US Census data into a useable lookup table for US cities
downloaded from http://www.census.gov/geo/maps-data/data/gazetteer2015.html
"""

import numpy as np
import polars as pl

from lemonade_stand.app_config import AppDir

DIRECTORIES = AppDir()


def get_state_cities() -> pl.DataFrame:
    """ """

    file_path = DIRECTORIES.root_dir / "2015_Gaz_place_national.txt"

    # Read data
    data_df = pl.read_csv(
        str(file_path), separator="\t", encoding="latin-1", use_pyarrow=False
    )

    places = data_df[["USPS", "NAME"]]  # TODO do this in one step

    # remove the place description
    regex = " CDP| city| town| village| borough| zona urbana| comunidad"
    places["NAME"] = places["NAME"].str.replace(
        regex, ""
    )  # TODO why does this give a warning?
    places.columns = ["state", "city"]

    # find all the states
    states = places["state"].unique()

    # actually want a list of every city in each state
    cities_df = pl.DataFrame(states, schema=["state"])
    cities_df["cities"] = np.empty((len(cities_df), 0)).tolist()
    for index, row in cities_df.iterrows():  # TODO vectorize this
        st = row["state"]
        cities_in_st = places.loc[places["state"] == st]
        cities_df["cities"][index] = cities_in_st["city"].tolist()

    # Return the dataframe
    return cities_df
