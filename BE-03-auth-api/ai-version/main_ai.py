# Quarantined AI Implementation (Stage 7 Review)
import os
from fastapi import FastAPI, HTTPException, Depends, Header
from supabase import create_client

app = FastAPI()
supabase = create_client(os.getenv("SUPABASE_URL", ""), os.getenv("SUPABASE_KEY", ""))

def get_user(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Access token required")
    token = authorization.replace("Bearer ", "")
    user = supabase.auth.get_user(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return user

@app.post("/auth/signup", status_code=201)
def signup(data: dict):
    if not data.get("email") or not data.get("password"):
        raise HTTPException(status_code=400, detail="Missing fields")
    return supabase.auth.sign_up({"email": data["email"], "password": data["password"]})

@app.post("/auth/login")
def login(data: dict):
    if not data.get("email") or not data.get("password"):
        raise HTTPException(status_code=400, detail="Missing fields")
    return supabase.auth.sign_in_with_password({"email": data["email"], "password": data["password"]})

@app.get("/protected/profile")
def profile(user = Depends(get_user)):
    return user
