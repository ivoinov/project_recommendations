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
├── requirements.txt        # List of project dependencies for easy replication.
```

## Installation

Ensure you have Python 3.6+ installed on your system. It's recommended to use a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

### Using `requirements.txt`

To install the required libraries and packages, use the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

This file contains a list of all necessary Python packages. If you want to replicate the environment on a different machine or deploy it to a server, this command will ensure that the exact versions of the packages used in development are installed.

### Creating and Updating `requirements.txt`

The `requirements.txt` file was generated using `pip freeze` and should be updated whenever new packages are installed or existing packages are upgraded:

```bash
pip freeze > requirements.txt
```

Remember to regenerate and commit the updated `requirements.txt` file to your version control system whenever you make changes to the project dependencies.

### Database Setup

#### PostgreSQL on macOS (using Homebrew)

- Install Homebrew if you haven't already:

  ```bash
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  ```

- Install PostgreSQL:

  ```bash
  brew install postgresql
  ```

- Start the PostgreSQL service:

  ```bash
  brew services start postgresql
  ```

- Connect to the default PostgreSQL database with:

  ```bash
  psql postgres
  ```

#### PostgreSQL on Ubuntu

- Update the package list:

  ```bash
  sudo apt update
  ```

- Install PostgreSQL:

  ```bash
  sudo apt install postgresql postgresql-contrib
  ```

- Start and enable the PostgreSQL service:

  ```bash
  sudo systemctl start postgresql
  sudo systemctl enable postgresql
  ```

- Connect to PostgreSQL with the `postgres` user:

  ```bash
  sudo -i -u postgres
  psql
  ```

## Running the Application

To start the FastAPI server:

```bash
uvicorn main:app --reload
```

The `--reload` flag is recommended for development as it enables hot reloading.

Access the API documentation by navigating to `http://127.0.0.1:8000/docs` in your web browser.


## API Endpoints

The application provides the following endpoints:

- `/signup`: Register a new user.
- `/login`: Authenticate and receive an access token.
- `/recommendations/`: Get product recommendations (requires authentication).

---
