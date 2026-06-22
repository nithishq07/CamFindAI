from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)

import os
origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")

# Allow CORS for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

from app.api.routes import auth, cameras, zones, identities, alerts, analytics, settings_api
from app.api.websockets import feeds, alerts_ws, status

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(cameras.router, prefix="/api/cameras", tags=["cameras"])
app.include_router(zones.router, prefix="/api/zones", tags=["zones"])
app.include_router(identities.router, prefix="/api/identities", tags=["identities"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["alerts"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(settings_api.router, prefix="/api/settings", tags=["settings"])

app.include_router(feeds.router, prefix="/ws/cameras", tags=["websockets"])
app.include_router(alerts_ws.router, prefix="/ws/alerts", tags=["websockets"])
app.include_router(status.router, prefix="/ws/status", tags=["websockets"])

@app.get("/")
def read_root():
    return {"message": f"Welcome to {settings.PROJECT_NAME} API"}
