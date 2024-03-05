import pandas as pd
from app.database import get_all_products
from sklearn.feature_extraction.text import TfidfVectorizer
import pickle
import os


def train_similar_model():
    global tfidf_matrices
    tfidf_matrices = {}
    # TODO:: Implement recalculate logic. Implement entity to store version, file name and recalculate logic.
    df_total = pd.DataFrame([product.as_dict() for product in get_all_products()])
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
        # df_cat['description'] = df_cat['description'].fillna(" ")
        tfidf_matrix = tfidf.fit_transform(df_cat["combined_description"])
        tfidf_matrices[cat] = {"tfidf_matrix": tfidf_matrix, "tfidf_vectorizer": tfidf}
    with open("product_recommender.pkl", "wb") as f:
        pickle.dump(tfidf_matrices, f)
