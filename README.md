# FastAPI Recommendation System

This project is a recommendation system built with FastAPI, focusing on providing upselling product recommendations ("people also buying with") and content-based recommendations based on product attributes. The system integrates with a PostgreSQL database for user and product data and uses machine learning models to generate recommendations.

## Project Structure

```
fastapi_recommendation_app/
│
├── main.py                 # Entry point for the FastAPI application.
├── models.py               # Contains declarative schema models for the database.
├── database.py             # Database connection and utility functions.
├── dependencies.py         # Dependency-related functions, such as user authentication.
│
├── routers/                # API routers, organizing endpoints into logical groups.
│   ├── auth.py             # Authentication-related endpoints.
│   ├── recommendations.py  # Endpoints for product recommendations.
│   ├── background.py       # Endpoints for background job processing.
│   └── schemas.py          # Models required for routing and request/response processing.
│── Dockerfile              # Instructions for building the Docker image for the application.
│── Dockerfile_celery       # Instructions for building the Docker image for the Celery worker.
│── magento_get_product_data.sql # SQL script for fetching product data from the Magento database.
│── magento_get_orders_stats.sql # SQL script for obtaining order statistics from the Magento database.
│── docker-compose.yml      # Docker Compose file to orchestrate the setup of multiple containers, including the   
|                             application, database, and any dependencies.
├── requirements.txt        # List of project dependencies for easy replication.
```

### New File: `routers/background.py`
This file introduces endpoints for managing background tasks, allowing for asynchronous execution of long-running operations without blocking the API's main thread. This is crucial for tasks such as data processing or batch updates that require significant processing time.

### Clarification on `models.py` and `routers/schemas.py`
- `models.py`: This file contains declarative schema models that define the structure of the database tables and their relationships. These models are essential for interacting with the database using SQLAlchemy.
- `routers/schemas.py`: This file contains Pydantic models that are used for request validation and response serialization. These schemas define the expected structure of request data and the format of responses sent back to the client, ensuring consistent and predictable API behavior.

### Enhanced Functionality
The addition of the `background.py` router and the `schemas.py` file within the `routers/` directory enhances the application's functionality and organization. The `background.py` router enables the application to handle tasks that are best run in the background, improving the overall performance and responsiveness of the API. The `schemas.py` file provides a centralized location for defining request and response models, streamlining the development and maintenance of the API's endpoints.


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

Update packages to the latest versions:

MacOS (make sure jq package installed ): 
```bash
pip list --outdated --format=json | jq -r '.[] | "\(.name)==\(.latest_version)"' | xargs -n1 pip install -U

OR

pip install -r requirements.txt --upgrade
```

Linux:
```bash
pip list --outdated --format=freeze | grep -v '^\-e' | cut -d = -f 1 | xargs -n1 pip install -U 

or 

pip install -r requirements.txt --upgrade
```
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

### To start the FastAPI server

```bash
uvicorn main:app --reload
```

The `--reload` flag is recommended for development as it enables hot reloading.

Access the API documentation by navigating to `http://127.0.0.1:8000/docs` in your web browser.

### RUN Celery APP
Celery is used in this project as a distributed task queue to manage background jobs without blocking the main application's execution. This is crucial for executing tasks that are resource-intensive or time-consuming, such as data processing or model training, ensuring the application remains responsive to user requests.

To run the Celery worker, use the following command:
bash
```bash
celery -A celery_app.worker worker --loglevel=info
```

This command starts a Celery worker that listens for tasks defined in the celery_app module.

## API Endpoints

The application provides the following endpoints:

- `/signup`: Register a new user.
- `/login`: Authenticate and receive an access token.
- `/recommendations/`: Get product recommendations (requires authentication).

---

### New Features and API Endpoints

#### Asynchronous Data Processing: `execute-background-task`
- **Endpoint**: `/execute-background-task`
- **Method**: POST
- **Description**: This endpoint allows for the execution of asynchronous background jobs for data processing. Users can initiate a job by providing a `job_name`, which will be processed in the background, allowing the API to respond immediately without waiting for the job to complete.
- **Usage**:
  ```bash
  curl -X 'POST' \
    'http://127.0.0.1:8000/execute-background-task' \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '{"job_name": "data_cleanup"}'
  ```

#### Upselling Recommendations
- **Endpoint**: `/upselling-recommendations/{product_id}`
- **Method**: GET
- **Description**: Fetch upselling product recommendations based on the purchase history of items related to the specified `product_id`. This feature enhances the customer's shopping experience by suggesting additional products that complement their current selection.
- **

Usage**:
  ```bash
  curl -X 'GET' \
    'http://127.0.0.1:8000/upselling-recommendations/12345' \
    -H 'accept: application/json'
  ```

#### Enhanced Authentication: `login`
- **Endpoint**: `/login`
- **Method**: POST
- **Description**: Authenticate users and receive a bearer token for accessing protected routes. The token should be included in the Authorization header of subsequent requests to endpoints requiring authentication.
- **Usage**:
  ```bash
  curl -X 'POST' \
    'http://127.0.0.1:8000/login' \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '{"username": "user", "password": "pass"}'
  ```

## Background Tasks

The project utilizes Celery for managing background tasks, improving performance and user experience by offloading heavy operations:

- **Data Synchronization**: Regular tasks that sync product and order data from Magento to our system, ensuring the recommendation engine uses up-to-date information.
- **Model Training**: Scheduled tasks that retrain the ML models with new data, keeping the recommendations relevant and accurate.

### Using SQL Scripts:

- The `magento_get_product_data.sql` and `magento_get_orders_stats.sql` scripts are executed as part of the data synchronization tasks to fetch the latest data from Magento.

### Dockerization:

- The application and Celery worker are containerized using Docker, simplifying deployment and scalability. The `Dockerfile` and `Dockerfile_celery` provide the necessary instructions to build the images, while `docker-compose.yml` orchestrates the containers' deployment.
