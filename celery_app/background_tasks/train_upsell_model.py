from lightfm import LightFM
from lightfm.data import Dataset
from app.database import get_orders, get_unique_customer_ids, get_unique_product_skus
from app.models import Order
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity


def train_upsell_model():
    global item_to_item
    dataset = Dataset()

    dataset.fit(get_unique_customer_ids(), get_unique_product_skus())
    user_mappings = dataset.mapping()[0]
    item_mappings = dataset.mapping()[2]

    len(user_mappings), len(item_mappings)

    # Create inverse mappings
    inv_user_mappings = {v: k for k, v in user_mappings.items()}
    inv_item_mappings = {v: k for k, v in item_mappings.items()}
    # Create an interactions matrix for each user, item and the weight
    # TODO:: replace empty element witht the actual data
    train_interactions, train_weights = dataset.build_interactions([])

    train_interactions.todense(), train_weights.todense()  # weights and interactions are the same if we just use 1s

    model = LightFM(
        no_components=100,  # the dimensionality of the feature latent embeddings
        learning_schedule="adagrad",  # type of optimiser to use
        loss="warp",  # loss type
        learning_rate=0.05,  # set the initial learning rate
        item_alpha=0.0,  # L2 penalty on item features
        user_alpha=0.0,  # L2 penalty on users features
        max_sampled=10,  # maximum number of negative samples used during WARP fitting
        random_state=123,
    )

    model.fit(train_interactions, epochs=20, verbose=True)  # our training data

    # Load latent representations to try computing predictions manually
    item_biases, item_embeddings = model.get_item_representations()

    # Find similar items
    item_to_item = pd.DataFrame(cosine_similarity(item_embeddings))
    item_to_item.index = item_mappings.keys()
    item_to_item.columns = item_mappings.keys()
