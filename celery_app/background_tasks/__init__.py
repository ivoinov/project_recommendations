# This is the __init__.py file in the root of your project

# Import any modules or packages you need here

# Define any global variables or constants here

# Define any functions or classes here

# You can also include any initialization code or setup logic here

# This file is executed when your project is imported as a package
# It can be used to set up the package's environment or perform any necessary setup tasks
try:
    from .products_processing import process_products_csv_file
    from .orders_processing import process_orders_csv_file
    from .train_upsell_model import train_upsell_model
    from .train_similar_model import train_similar_model
except Exception:
    process_products_csv_file = None
    process_orders_csv_file = None
    train_upsell_model = None
    train_similar_model = None
