import pickle
import time
from app.models import Order
from app.database import get_orders_aggregated_data_query, SessionLocal
import pandas as pd
from surprise import Dataset, SVD, Reader, KNNBasic
from surprise.model_selection import train_test_split


def train_upsell_model():
    # Convert the query result into a pandas DataFrame
    df = pd.read_sql(get_orders_aggregated_data_query().statement, SessionLocal().bind)
    # Determine the rating scale
    min_rating = df["rating"].min()
    max_rating = df["rating"].max()
    # Define a reader with the rating scale
    reader = Reader(rating_scale=(min_rating, max_rating))
    # Load the dataset from the DataFrame
    data = Dataset.load_from_df(df[["user_id", "item_id", "rating"]], reader)
    # Split the data into train and test sets
    trainset, _ = train_test_split(data, test_size=0.2)
    # Train the SVD model
    algo_svd = SVD(reg_all=0.2)
    algo_svd.fit(trainset)
    trained_svd_model = algo_svd
    # Save the trained model to a file
    timestamp = int(time.time())
    with open(f"trained_svd_model.pkl", "wb") as f:
        pickle.dump(trained_svd_model, f)
    # Save also trainset to a file
    with open(f"svd_model_trainset.pkl", "wb") as f:
        pickle.dump(trainset, f)
