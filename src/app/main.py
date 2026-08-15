import os
from ..utils.logger import initialize_logger
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import linescorigami_routes

load_dotenv()
os.makedirs("./logs", exist_ok=True)
initialize_logger()

app = FastAPI()
app.include_router(linescorigami_routes.router)
