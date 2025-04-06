from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from app.database import users_collection
from app.models import User, UpdateUser,LoginRequest
from app.auth import verify_password, get_password_hash, create_access_token, decode_access_token
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()
origins = [
    "https://cryptodashboardmayu.netlify.app",  # your deployed frontend
    "http://localhost:3000",                    # optional: for local dev
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,           
    allow_credentials=True,
    allow_methods=["*"],              # allow all methods (GET, POST, etc.)
    allow_headers=["*"],              # allow all headers
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
def login(request: LoginRequest):
    user = users_collection.find_one({"email": request.email})
    if not user or not verify_password(request.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token({"sub": request.email})
    return {"token": access_token, "user": {"email": request.email}}

@app.get("/auth/getuser")
def get_user(token: str = Depends(oauth2_scheme)):
    email = decode_access_token(token)
    if not email:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = users_collection.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {"email": email, "wishlist": user.get("wishlist", [])}


@app.put("/auth/add-to-wishlist")
def add_to_wishlist(item: dict, token: str = Depends(oauth2_scheme)):
    email = decode_access_token(token)
    if not email:
        raise HTTPException(status_code=401, detail="Invalid token")

    users_collection.update_one({"email": email}, {"$push": {"wishlist": item}})
    return {"message": "Item added to wishlist"}

@app.delete("/auth/remove-from-wishlist")
def remove_from_wishlist(item: dict,token: str = Depends(oauth2_scheme)):
    email=decode_access_token(token)
    if not email:
        raise HTTPException(status_code=401,detail="Invalid token")
    users_collection.update_one({"email":email},{"$pull":{"wishlist":item}})
    return {"message":"Item removed from wishlist"}


@app.get("/")
def read_root():
    return {"message": "Hello from Render!"}