from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.database import users_collection
from app.models import User, UpdateUser
from app.auth import verify_password, get_password_hash, create_access_token, decode_access_token
from typing import List
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  #  frontend URL (e.g., "http://localhost:3000")
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE)
    allow_headers=["*"],  # Allow all headers
)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

@app.post("/auth/register")
def register_user(user: User):
    existing_user = users_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    hashed_password = get_password_hash(user.password)
    new_user = {"email": user.email, "password": hashed_password, "wishlist": []}
    users_collection.insert_one(new_user)

    return {"message": "User registered successfully"}

@app.post("/auth/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = users_collection.find_one({"email": form_data.username})
    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token({"sub": form_data.username})
    return {"token": access_token, "user": {"email": form_data.username}}

@app.get("/auth/getuser")
def get_user(token: str = Depends(oauth2_scheme)):
    email = decode_access_token(token)
    if not email:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = users_collection.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {"email": email, "wishlist": user.get("wishlist", [])}

@app.put("/auth/update")
def update_user(update_data: UpdateUser, token: str = Depends(oauth2_scheme)):
    email = decode_access_token(token)
    if not email:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = users_collection.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    update_fields = {}
    if update_data.new_email:
        update_fields["email"] = update_data.new_email
    if update_data.new_password:
        update_fields["password"] = get_password_hash(update_data.new_password)
    if update_data.wishlist is not None:
        update_fields["wishlist"] = update_data.wishlist

    users_collection.update_one({"email": email}, {"$set": update_fields})
    return {"message": "Profile updated successfully"}

@app.post("/auth/add-to-wishlist")
def add_to_wishlist(item: str, token: str = Depends(oauth2_scheme)):
    email = decode_access_token(token)
    if not email:
        raise HTTPException(status_code=401, detail="Invalid token")

    users_collection.update_one({"email": email}, {"$push": {"wishlist": item}})
    return {"message": "Item added to wishlist"}
