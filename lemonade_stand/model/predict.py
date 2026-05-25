""" """

from collections.abc import Callable

import numpy as np
import polars as pl
from sklearn.metrics.pairwise import cosine_similarity

from .utils import ModelData


def predict_cosine_similarity(
    func_vectorize: Callable,
    data_model: ModelData,
) -> pl.LazyFrame:
    """Utilizes cosine similarity between train and test vectors to predict the category of the output data."""

    train_dataframe = data_model.train_data.collect()

    train_vector, test_vector = func_vectorize(
        train_series=train_dataframe.select(pl.col(data_model.text_field)).to_series(),
        test_series=data_model.inference_data.select(pl.col(data_model.text_field))
        .collect()
        .to_series(),
    )

    similarity = cosine_similarity(test_vector, train_vector)
    label_index = np.argmax(similarity, axis=1)

    return data_model.inference_data.with_columns(
        predicted=train_dataframe[label_index, data_model.label_field]
    )
