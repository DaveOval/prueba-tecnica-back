import os
from dotenv import load_dotenv

load_dotenv()
# MongoDB Settings
MONGO_URI = os.getenv("MONGO_URI")

# Allowed origins for CORS
ALLOWED_ORIGINS = os.getenv("FRONTEND_URL")

# JWT Settings
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours

# Formats and size validations
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB