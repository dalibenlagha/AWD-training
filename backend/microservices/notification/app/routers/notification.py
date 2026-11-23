"""Notification routes: /api/notifications/..."""
import httpx
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from app import eureka
from app.schemas import CandidateFromEureka, HelloResponse

router = APIRouter(prefix="/api/notifications", tags=["Notifications"])


@router.get(
    "/hello",
    response_model=HelloResponse,
    summary="Hello from the notification microservice",
    description="Checks that the microservice is up and returns a greeting message.",
)
def hello() -> HelloResponse:
    return HelloResponse(message="hello I'm microservice notification")


@router.get(
    "/candidates/{candidate_id}",
    response_model=CandidateFromEureka,
    tags=["Eureka"],
    summary="Get a candidate from the candidat microservice, found through Eureka",
    description=(
        "Bonus Eureka: asks Eureka for an instance of CANDIDAT (no hard-coded URL), "
        "then calls GET /api/candidates/{id} on it. `servedBy` shows which instance answered."
    ),
    responses={
        404: {"description": "Candidate not found (answer of the candidat microservice)"},
        503: {"description": "No CANDIDAT instance in Eureka, or the instance is not reachable"},
    },
)
async def get_candidate(candidate_id: int):
    # 1 + 2. Ask Eureka (local copy of the registry) for the address of one CANDIDAT instance
    base_url = eureka.find_service_url("CANDIDAT")
    if base_url is None:
        raise HTTPException(status_code=503, detail="No instance of CANDIDAT is registered in Eureka")

    # 3. Call that instance directly (short timeout: never wait forever for another service)
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get(f"{base_url}/api/candidates/{candidate_id}")
    except httpx.HTTPError:
        raise HTTPException(status_code=503, detail=f"CANDIDAT instance {base_url} is not reachable")

    if response.status_code != 200:
        # e.g. 404 sent back by candidat
        try:
            body = response.json()
        except ValueError:
            body = {"detail": response.text}
        return JSONResponse(status_code=response.status_code, content=body)

    # servedBy shows which CANDIDAT instance answered (useful with 2 instances: 8081 and 8091)
    return CandidateFromEureka(servedBy=base_url, candidate=response.json())


# TODO (students): implement the Notification logic.
# No database: keep notifications in memory, for example:
#
# notifications: list[Notification] = []
# next_id = 1
#
# @router.get("", response_model=list[Notification], summary="List notifications")
# def find_all(): ...
#
# @router.get("/{notification_id}", response_model=Notification, summary="Get a notification")
# def find_by_id(notification_id: int): ...            # raise HTTPException(404, ...) if not found
#
# @router.post("", response_model=Notification, status_code=201, summary="Create a notification")
# def create(body: NotificationCreate): ...
#
# @router.put("/{notification_id}", response_model=Notification, summary="Update a notification")
# def update(notification_id: int, body: NotificationCreate): ...
#
# @router.patch("/{notification_id}/send", response_model=Notification, summary="Mark as sent")
# def send(notification_id: int): ...
#
# @router.delete("/{notification_id}", status_code=204, summary="Delete a notification")
# def delete(notification_id: int): ...
#
# Swagger is generated automatically from these decorators and the Pydantic schemas.
