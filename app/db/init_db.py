from mongoengine import connect, disconnect
from app.config import MONGO_URI
from app.models.user import User
from app.models.images import Image

def migrate_image_data():
    try:
        # Get all images that have transformations field
        images = Image.objects(__raw__={'transformations': {'$exists': True}})
        
        for image in images:
            # Get the first transformation if it exists
            if image.transformations and len(image.transformations) > 0:
                image.filter_name = image.transformations[0]
                # If it's brightness, try to get the value
                if image.filter_name == 'brightness' and len(image.transformations) > 1:
                    try:
                        image.filter_value = str(float(image.transformations[1]))
                    except:
                        image.filter_value = None
            else:
                image.filter_name = None
                image.filter_value = None
            
            # Remove the old field
            image._data.pop('transformations', None)
            image.save()
            
        print("Image data migration completed successfully.")
    except Exception as e:
        print(f"Error during image data migration: {str(e)}")

def init_db():
    try:
        # Connect to the MongoDB database
        connect(host=MONGO_URI, db='imgbest')
        
        # Check if the database is empty
        if not User._get_collection().count_documents({}):
            print("Initializing database...")
            pass
            
        # Run migration for existing images
        migrate_image_data()
            
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Error initializing data base: {str(e)}")
        raise e

def close_db():
    disconnect() 