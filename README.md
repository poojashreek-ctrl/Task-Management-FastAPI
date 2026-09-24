Task Management Application


A Task REST API built using FastAPI, PostgreSQL, SQLAlchemy, Alembic, JWT authentication, and Pytest.


Features

1.User registration
2.User login with JWT authentication
3.Create tasks
4.Get all tasks
5.Get a single task
6.Update tasks
7.Delete tasks
8.Task filtering by status and priority
9.Pagination using limit and offset
10.Sorting by due date or creation date
11.User-based task authorization
12.Automatic API documentation with Swagger
13.Automated tests using Pytest

Requirements

1.Python
2.PostgreSQL
3.pip
4.Virtual environment

Project Setup

1. Clone the project
git clone <repository-url>

2. Create a virtual environment
python3 -m venv fastapienv

Activate it on macOS/Linux:
source fastapienv/bin/activate

3. Install dependencies
pip install -r requirements.txt

4. Create PostgreSQL database
Create a PostgreSQL database for the application.
Example:

CREATE DATABASE TaskapplicationDatabase;

5. Configure environment variables
Copy .env.example to .env:
cp .env.example .env

Update .env with your PostgreSQL credentials and JWT configuration.
Example:

DATABASE_URL=postgresql://postgres:your_password@localhost/TaskapplicationDatabase
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=20

also update postgresql in alembic.ini

6. Run database migrations
alembic upgrade head

7. Start the FastAPI application
uvicorn TodoApp.main:app --reload

The application will be available at:
http://127.0.0.1:8000

API Documentation
FastAPI provides interactive Swagger documentation at:
http://127.0.0.1:8000/docs

You can use the Swagger UI to:

1.Register a user.
2.Login using /token.
3.Click lock icon in task apis.
4.Enter username and password.
5.Use the CRUD 


Running Tests

Run all tests:
pytest

The tests cover:
Authentication
Task creation
Reading tasks
Updating tasks
Deleting tasks
Authorization
Accessing another user's task
Database Migrations

Environment Variables
See .env.example for the required environment variables.
