from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(title="Allergen Detection API")

app.include_router(router) 