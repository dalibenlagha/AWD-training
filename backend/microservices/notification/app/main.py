"""Notification microservice - entry point.

Run:  python -m app.main                                 (port 8084, or the PORT environment variable)
  or: python -m uvicorn app.main:app --reload --port 8084
      (with uvicorn, set PORT to the same value as --port, otherwise Eureka gets a wrong port)
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.eureka import PORT, start_eureka, stop_eureka
from app.routers import notification
from app.schemas import HealthResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start-up: register in Eureka
    await start_eureka()
    yield
    # Shutdown (Ctrl+C): de-register from Eureka
    await stop_eureka()


app = FastAPI(
    title="Notification Microservice API",
    version="1.0.0",
    description=(
        "Notification microservice (Python / FastAPI, no database). "
        "Only the hello endpoint is implemented; the notification logic is to be developed by students."
    ),
    contact={"name": "Badia Abouhdid"},
    servers=[{"url": f"http://localhost:{PORT}", "description": "Local"}],
    # Same URLs as the other microservices of the project
    docs_url="/swagger-ui",       # Swagger UI
    openapi_url="/v3/api-docs",   # OpenAPI JSON
    redoc_url="/redoc",           # alternative documentation
    lifespan=lifespan,            # code run at start-up and at shutdown (Eureka registration)
)

app.include_router(notification.router)

# TODO (students): if you add other routers, include them here.


@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["Eureka"],
    summary="Health of the instance",
    description="Bonus Eureka: declared to Eureka as healthCheckUrl and statusPageUrl.",
)
def health() -> HealthResponse:
    return HealthResponse(status="UP")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=PORT, reload=True)
