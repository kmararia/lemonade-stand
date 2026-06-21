"""
A module for vectorizing text data using
    1. TF-IDF (Term Frequency-Inverse Document Frequency)
"""

import polars as pl
from sklearn.feature_extraction.text import TfidfVectorizer


def vectorize_tfidf(train_series: pl.Series, test_series: pl.Series):
    """Vectorizes a specified field in a polars DataFrame using TF-IDF."""

    vectorizer = TfidfVectorizer(lowercase=True, stop_words="english")

    train_vector = vectorizer.fit_transform(train_series.to_list())
    test_vector = vectorizer.transform(test_series.to_list())

    return train_vector.toarray(), test_vector.toarray()
