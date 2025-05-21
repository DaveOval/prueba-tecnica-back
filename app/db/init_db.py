from mongoengine import connect, disconnect
from app.config import MONGO_URI
from app.models.user import User

def init_db():
    try:
        # Connect to the MongoDB database
        connect(host=MONGO_URI, db='imgbest')
        
        # Check if the database is empty
        if not User._get_collection().count_documents({}):
            print("Initializing database...")
            pass
            
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Error initializing data base: {str(e)}")
        raise e

def close_db():
    disconnect() 