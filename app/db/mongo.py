from mongoengine import connect
from app.config import MONGO_URI

connect(host=MONGO_URI)