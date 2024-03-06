import pandas as pd
from app.database import get_all_products
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MinMaxScaler
from app.config import settings
import pickle
import os


## This is the global variable that will store the similarity matrix and product index mapping
def train_similar_model():
    global df_total
    df_total = pd.DataFrame([product.as_dict() for product in get_all_products()])
    calculate_description_matrices()
    calculate_price_vector()
    # TODO:: Implement recalculate logic. Implement entity to store version, file name and recalculate logic.


def calculate_description_matrices():
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
    with open(settings.description_tfidf_file_name, "wb") as f:
        pickle.dump(settings.description_tfidf_matrices, f)


def calculate_price_vector():
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


def load_price_vector():
    if os.path.isfile(settings.price_vector_file_name):
        with open(settings.price_vector_file_name, "rb") as file:
            return pickle.load(file)
    return []
