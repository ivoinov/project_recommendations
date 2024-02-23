import pandas as pd
from app.database import get_product_by_categories
from sklearn.feature_extraction.text import TfidfVectorizer
import pickle
import os.path
from sklearn.metrics.pairwise import linear_kernel


def train_similar_model():
    # TODO:: Implement recalculate logic. Implement entity to store version, file name and recalculate logic.
    recalculate = True
    if not recalculate and os.path.isfile("tfidf_matrices.pkl"):
        # Load saved TF-IDF matrices and vectorizers from file
        with open("tfidf_matrices.pkl", "rb") as file:
            tfidf_matrices = pickle.load(file)
        return tfidf_matrices
    tfidf_matrices = {}
    products_by_category = get_product_by_categories()
    for cat, descriptions in products_by_category:
        # Extract descriptions from the fetched products
        descriptions = [desc for desc in descriptions if desc]
        # Initialize a TF-IDF vectorizer
        tfidf = TfidfVectorizer(stop_words="english")
        # Compute TF-IDF matrix for the descriptions
        tfidf_matrix = tfidf.fit_transform(descriptions)
        # Store TF-IDF matrix and vectorizer in the tfidf_matrices dictionary
        tfidf_matrices[cat] = {"tfidf_matrix": tfidf_matrix, "tfidf_vectorizer": tfidf}
        # Save TF-IDF matrices and vectorizers to file
        with open("tfidf_matrices.pkl", "wb") as file:
            pickle.dump(tfidf_matrices, file)

    return tfidf_matrices
