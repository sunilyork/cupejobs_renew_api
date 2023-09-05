import logging.config
import os

import uvicorn
import yaml
from fastapi import FastAPI
from fastapi import Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from apps.admin.routers import router as admin_router
from apps.alerts.routers import router as alerts_router
from apps.config import ROOT_DIR, get_settings
from apps.cupe1assns.routers import router as cupe1assns_router
from apps.cupejobsproj.jobs.views import router as cupejobs_router
from apps.db.mongo_setup import init_database_connection
from apps.faculty.routers import router as faculty_router
from apps.notifications.routers import router as notifications_router
from apps.nra_cssp.routers import router as nra_router
from apps.postings.routers import router as postings_router
from apps.users.routers import router as users_router

with open(os.path.join(ROOT_DIR, "logging_config.yaml"), "rt") as f:
    config = yaml.safe_load(f.read())

logging.config.dictConfig(config)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="CUPE Jobs API", description="Contract Academic Employment Opportunities"
)
settings = get_settings()

origins = [settings.CUPEJOBS_UI_URL]


@app.on_event("startup")
async def startup_db_client():
    app.mongodb_client = await init_database_connection()
    app.mongodb = app.mongodb_client[settings.DB_NAME]


@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongodb_client.close()


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin_router, tags=["admin"], prefix="/admin")
app.include_router(cupe1assns_router, tags=["cupe1assns"], prefix="/cupe1assns")
app.include_router(cupejobs_router, tags=["jobs"], prefix="/jobs")
app.include_router(nra_router, tags=["nra"], prefix="/nra")
app.include_router(alerts_router, tags=["alerts"], prefix="/alerts")
app.include_router(faculty_router, tags=["faculty"], prefix="/faculty")
app.include_router(postings_router, tags=["postings"], prefix="/postings")
app.include_router(users_router, tags=["users"], prefix="/users")
app.include_router(
    notifications_router, tags=["notifications"], prefix="/notifications"
)


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(
    request: Request, exc: RequestValidationError
):
    print(f" {status.HTTP_422_UNPROCESSABLE_ENTITY}: {exc.errors()}")
    print(f" Body: {exc.body}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
    )


@app.get("/", include_in_schema=False)
async def root():
    return {"message": "Welcome to the CUPE Jobs API"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        reload=settings.DEBUG_MODE,
        port=settings.PORT,
    )
