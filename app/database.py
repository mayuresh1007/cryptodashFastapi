import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB Connection
uri = os.getenv("MONGO_URI")
if not uri:
    raise ValueError("Error: MONGO_URI is not set in the environment variables.")

try:
    client = MongoClient(uri, server_api=ServerApi('1'))
    db = client["datamongo"]  # Database
    users_collection = db["users"]  # Collection

    # Test Connection
    client.admin.command('ping')
    print("✅ Connected to MongoDB!")
except Exception as e:
    print("🚨 MongoDB Connection Error:", e)
    raise




# uri = "mongodb+srv://Mayuresh:mk1234@cluster0.caduy.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# # Create a new client and connect to the server
# client = MongoClient(uri, server_api=ServerApi('1'))

# # Send a ping to confirm a successful connection
# try:
#     client.admin.command('ping')
#     print("Pinged your deployment. You successfully connected to MongoDB!")
# except Exception as e:
#     print(e)