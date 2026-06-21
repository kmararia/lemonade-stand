""" """

from collections.abc import Callable
from pathlib import Path

import polars as pl

from lemonade_stand.config import UserConfig
from lemonade_stand.utils import set_up_logger

from .predict import predict_cosine_similarity
from .utils import ModelData
from .vectorize import vectorize_tfidf

LOGGER = set_up_logger(Path(__file__).stem)


def predict_buckets(
    config: UserConfig, input_data: pl.LazyFrame, func_field_cleaner: Callable
) -> ModelData:
    """ """

    model_data = ModelData(
        inference_data=input_data,
        train_data=config.model.training_file,
        func_field_cleaner=func_field_cleaner,
    )

    return_df = predict_cosine_similarity(
        func_vectorize=vectorize_tfidf,
        data_model=model_data,
    )

    model_data.inference_data = return_df.with_columns(
        category=pl.col("predicted")
    ).drop("predicted")

    return model_data


# Expose only the predicted data
__all__ = ["predict_buckets"]
