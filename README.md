### Setup Instructions:

1. Clone the repository
2. Create a .env file and set variables respectively to .env.example
3. Run the migrations using `alembic upgrade head` and check out your tables
4. Run the application inside app/ using `uvicorn main:app --reload`