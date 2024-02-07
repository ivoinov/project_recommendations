# FastAPI Recommendation System

This project is a recommendation system built with FastAPI, focusing on providing upselling product recommendations ("people also buying with") and content-based recommendations based on product attributes. The system integrates with a PostgreSQL database for user and product data and uses machine learning models to generate recommendations.

## Project Structure

```
fastapi_recommendation_app/
│
├── main.py                 # Entry point for the FastAPI application.
├── models.py               # Pydantic models for request and response validation.
├── database.py             # Database connection and utility functions.
├── dependencies.py         # Dependency-related functions, such as user authentication.
│
├── routers/                # API routers, organizing endpoints into logical groups.
│   ├── auth.py             # Authentication-related endpoints.
│   └── recommendations.py  # Endpoints for product recommendations.
│
└── data_processing/        # Scripts for data processing and machine learning model training.
    └── train_model.py      # Script for training the recommendation model.
```

## Installation

Ensure you have Python 3.6+ installed on your system. It's recommended to use a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

Install the required libraries and packages:

```bash
pip install fastapi uvicorn databases[postgresql] sqlalchemy sklearn numpy joblib
```

### Key Dependencies

- **FastAPI**: Modern, fast web framework for building APIs with Python.
- **Uvicorn**: ASGI server for running FastAPI.
- **Databases**: Provides async database support.
- **SQLAlchemy**: SQL toolkit and ORM for Python.
- **Scikit-learn**: Machine learning library for Python, used for model training and similarity calculations.
- **NumPy**: Fundamental package for scientific computing in Python.
- **Joblib**: Efficient tools for saving and loading Python objects.

## Running the Application

1. **Database Setup**: Ensure your PostgreSQL database is configured according to `database.py`. Create necessary tables and populate them with initial data.

2. **Model Training**: Navigate to the `data_processing` directory and run the `train_model.py` script to train your machine learning model and generate the product similarity matrix.

    ```bash
    python data_processing/train_model.py
    ```

3. **Start the FastAPI Application**: Run the following command from the root directory of the project:

    ```bash
    uvicorn main:app --reload
    ```

    The `--reload` flag enables hot reloading during development.

## API Endpoints

- **Token**: `POST /token` - Authenticate users and return an access token.
- **Upselling Recommendations**: `GET /upselling-recommendations/{product_id}` - Retrieve upselling product recommendations based on the provided product ID.
- Additional endpoints and functionality can be added by expanding the routers in the `routers` directory.

## Notes

- Ensure to replace mock data and placeholders with actual implementation details specific to your project.
- Regularly update your machine learning models with new data to maintain the relevance of recommendations.

---
