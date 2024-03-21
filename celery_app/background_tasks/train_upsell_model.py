import pickle
import pandas as pd
from surprise import Dataset, SVD, Reader, KNNBasic, accuracy
from surprise.model_selection import train_test_split
from app.repositories import OrderRepository, ProductRepository
from app.services import OrderService, ProductService
from app.config import settings, db_settings
from sqlalchemy.orm import Session

# Configuration (Consider moving these to a separate config file or environment variables)
TRAIN_TEST_SPLIT_RATIO = 0.2
REG_ALL = 0.2
SIM_OPTIONS = {"name": "cosine", "user_based": False}


def load_data(db: Session):
    try:
        order_repository = OrderRepository(db)
        order_service = OrderService(order_repository)
        # query = order_service.get_order_aggregated_data_query()
        df = pd.DataFrame(order_repository.fetch_all_orders())
        return df
    except Exception as e:
        settings.logger.error(f"Error loading data: {e}")
        raise


def prepare_dataset(df: pd.DataFrame, db: Session):
    try:
        product_service = ProductService(ProductRepository(db))
        # Validate DataFrame structure
        if not all(col in df.columns for col in ["increment_id", "item_sku", "rating"]):
            raise ValueError(
                "DataFrame must contain 'increment_id', 'item_sku', and 'rating' columns."
            )

        df["rating"] = df["rating"].apply(update_rating_column).astype(float)
        df["increment_id"] = df["increment_id"].astype(str)
        df["item_sku"] = df["item_sku"].apply(
            lambda x: product_service.get_product_id_by_sku(x)
        )
        min_rating, max_rating = df["rating"].min(), df["rating"].max()
        reader = Reader(rating_scale=(min_rating, max_rating))
        data = Dataset.load_from_df(df[["increment_id", "item_sku", "rating"]], reader)
        return data
    except Exception as e:
        settings.logger.error(f"Error preparing dataset: {e}")
        raise


def train_models(data):
    try:
        trainset, testset = train_test_split(data, test_size=TRAIN_TEST_SPLIT_RATIO)
        # # Train SVD model
        # algo_svd = SVD(reg_all=REG_ALL)
        # algo_svd.fit(data.build_full_trainset())
        # predictions_svd = algo_svd.test(testset)
        # accuracy.rmse(predictions_svd)
        # Train KNN model
        algo_knn = KNNBasic(sim_options=SIM_OPTIONS)
        try:
            algo_knn.fit(trainset)
        except Exception as e:
            settings.logger.error(f"Error during KNN training: {e}")
            raise
        predictions_knn = algo_knn.test(testset)
        accuracy.rmse(predictions_knn)

        return algo_knn, trainset
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
    data = prepare_dataset(df, db)
    trained_knn_model, trainset = train_models(data)
    # save_model(trained_svd_model, "trained_svd_model.pkl")
    save_model(trained_knn_model, "trained_knn_model.pkl")
    # save_model(trainset, "svd_model_trainset.pkl")
    settings.logger.info("Model training completed successfully.")


def update_rating_column(x):
    result = 100
    if float(x) > 0:
        result = x * 100
    return round(abs(result), 2)
