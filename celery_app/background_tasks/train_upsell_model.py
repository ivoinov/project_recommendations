import pickle
import pandas as pd
from surprise import Dataset, SVD, Reader, KNNBasic, accuracy
from surprise.model_selection import train_test_split
from app.repositories import OrderRepository
from app.config import settings, db_settings
from sqlalchemy.orm import Session

# Configuration (Consider moving these to a separate config file or environment variables)
TRAIN_TEST_SPLIT_RATIO = 0.2
REG_ALL = 0.2
SIM_OPTIONS = {"name": "cosine", "user_based": False, "k": 10, "min_support": 3}
GUEST_USER_ID = -1  # Assign a fixed user ID for guest orders

def load_data(db: Session):
    try:
        order_repository = OrderRepository(db)
        query = order_repository.get_order_aggregated_data_query()
        df = pd.read_sql(query.statement, db.bind)
        # Handle guest orders by assigning a fixed user ID
        df['user_id'] = df['user_id'].fillna(GUEST_USER_ID)
        return df
    except Exception as e:
        settings.logger.error(f"Error loading data: {e}")
        raise

def prepare_dataset(df: pd.DataFrame):
    try:
        # Validate DataFrame structure
        if not all(col in df.columns for col in ['user_id', 'item_id', 'rating']):
            raise ValueError("DataFrame must contain 'user_id', 'item_id', and 'rating' columns.")
        
        min_rating, max_rating = df['rating'].min(), df['rating'].max()
        reader = Reader(rating_scale=(min_rating, max_rating))
        data = Dataset.load_from_df(df[['user_id', 'item_id', 'rating']], reader)
        return data
    except Exception as e:
        settings.logger.error(f"Error preparing dataset: {e}")
        raise

def train_models(data):
    try:
        trainset, testset = train_test_split(data, test_size=TRAIN_TEST_SPLIT_RATIO)

        # Train SVD model
        algo_svd = SVD(reg_all=REG_ALL)
        algo_svd.fit(trainset)
        predictions_svd = algo_svd.test(testset)
        accuracy.rmse(predictions_svd)

        # Train KNN model
        algo_knn = KNNBasic(sim_options=SIM_OPTIONS)
        try:
            algo_knn.fit(trainset)
        except Exception as e:
            settings.logger.error(f"Error during KNN training: {e}")
            raise
        predictions_knn = algo_knn.test(testset)
        accuracy.rmse(predictions_knn)
        
        return algo_svd, algo_knn, trainset
    except Exception as e:
        settings.logger.error(f"Error training model: {e}")
        raise

def save_model(model, filename):
    try:
        with open(filename, "wb") as f:
            pickle.dump(model, f)
    except Exception as e:
        settings.logger.error(f"Error saving model {filename}: {e}")
        raise

def train_upsell_model():
    db = next(db_settings.get_db())
    df = load_data(db)
    data = prepare_dataset(df)
    trained_svd_model, trained_knn_model, trainset = train_models(data)
    save_model(trained_svd_model, "trained_svd_model.pkl")
    save_model(trained_knn_model, "trained_knn_model.pkl")
    save_model(trainset, "svd_model_trainset.pkl")
    settings.logger.info("Model training completed successfully.")

