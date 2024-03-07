import pandas as pd
from app.database import get_all_products
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MinMaxScaler
from app.config import settings
import pickle
import os
import numpy as np


## This is the global variable that will store the similarity matrix and product index mapping
def train_similar_model():
    global df_total
    df_total = pd.DataFrame([product.as_dict() for product in get_all_products()])
    calculate_description_and_price_matrices()
    # calculate_price_vector()
    # TODO:: Implement recalculate logic. Implement entity to store version, file name and recalculate logic.


def calculate_description_and_price_matrices():
    category_list = set(df_total["parent_category"])
    for cat in category_list:
        df_cat = df_total[df_total["parent_category"] == cat]
        tfidf = TfidfVectorizer(stop_words="english")
        df_cat = df_cat.copy()
        # Concatenate description and short_description into a new column
        df_cat["combined_description"] = (
            df_cat["description"].fillna("")
            + " "
            + df_cat["short_description"].fillna("")
        )
        tfidf_matrix = tfidf.fit_transform(df_cat["combined_description"])
        settings.description_tfidf_matrices[cat] = {
            "tfidf_matrix": tfidf_matrix,
            "tfidf_vectorizer": tfidf,
        }

        # Price vector processing
        scaler = MinMaxScaler()
        # Handle NaN or infinite values in the price column
        df_cat["price"] = df_cat["price"].fillna(df_cat["price"].mean())
        df_cat = df_cat[np.isfinite(df_cat["price"])]
        normalized_prices = scaler.fit_transform(df_cat[["price"]])
        settings.price_vectors[cat] = normalized_prices.flatten()

    with open(settings.description_tfidf_file_name, "wb") as f:
        pickle.dump(settings.description_tfidf_matrices, f)
    with open(settings.price_vector_file_name, "wb") as f:
        pickle.dump(settings.price_vectors, f)


# This function calculates the price vector (general for all products) and stores it in a file
def calculate_price_vector():
    # Check for and handle NaN or infinite values in the price column
    # Fill NaN values with the mean price
    df_total["price"].fillna(df_total["price"].mean(), inplace=True)
    # Remove any infinite values, if present
    df_total = df_total[np.isfinite(df_total["price"])]
    # Extract the price column into a separate DataFrame
    price_df = df_total[["price"]].copy()
    # Initialize a Min-Max Scaler
    scaler = MinMaxScaler()
    # Fit and transform the prices to be between 0 and 1
    normalized_prices = scaler.fit_transform(price_df)
    # The normalized_prices array is now your price vector
    settings.price_vector = (
        normalized_prices.flatten()
    )  # Flatten to convert it from 2D to 1D array if necessary
    with open(settings.price_vector_file_name, "wb") as f:
        pickle.dump(settings.price_vector, f)


def load_description_matrices():
    if os.path.isfile(settings.description_tfidf_file_name):
        with open(settings.description_tfidf_file_name, "rb") as file:
            return pickle.load(file)
    return {}


def load_price_vectors():
    if os.path.isfile(settings.price_vector_file_name):
        with open(settings.price_vector_file_name, "rb") as file:
            return pickle.load(file)
    return []
