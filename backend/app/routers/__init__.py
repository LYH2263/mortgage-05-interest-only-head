from fastapi import APIRouter
from app.routers import dashboard, history, interest_only, loans, schedule, settings
api = APIRouter(prefix="/api")
for r in (dashboard, loans, schedule, history, settings, interest_only): api.include_router(r.router)
