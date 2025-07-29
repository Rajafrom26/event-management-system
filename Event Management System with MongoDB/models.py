from pymongo import MongoClient
from flask_bcrypt import Bcrypt

client = MongoClient("mongodb://localhost:27017/")
db = client["event_management"]

bcrypt = Bcrypt()

# Collections
users = db["users"]
events = db["events"]
