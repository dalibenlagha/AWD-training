"""Pydantic schemas: they validate data AND generate the Swagger documentation."""
from pydantic import BaseModel, Field


class HelloResponse(BaseModel):
    message: str = Field(..., examples=["hello I'm microservice notification"])


class HealthResponse(BaseModel):
    """Bonus Eureka: answer of GET /health."""
    status: str = Field(..., examples=["UP"])


class CandidateFromEureka(BaseModel):
    """Bonus Eureka: a candidate read from the candidat microservice, found through Eureka."""
    servedBy: str = Field(..., examples=["http://192.168.1.10:8081"])
    candidate: dict = Field(
        ..., examples=[{"id": 1, "firstname": "Badia", "lastname": "Abouhdid", "email": "badia@example.com"}]
    )


# TODO (students): add the Notification schemas, for example:
#
# from datetime import datetime
# from enum import Enum
#
# class NotificationType(str, Enum):
#     EMAIL = "EMAIL"
#     SMS = "SMS"
#
# class NotificationStatus(str, Enum):
#     PENDING = "PENDING"
#     SENT = "SENT"
#
# class NotificationCreate(BaseModel):          # request body (POST / PUT)
#     recipient: str = Field(..., min_length=1, examples=["badia@example.com"])
#     subject: str = Field(..., min_length=1, max_length=150, examples=["Interview scheduled"])
#     message: str = Field(..., min_length=1, examples=["Your interview is on 2026-10-05 at 10:00"])
#     type: NotificationType = NotificationType.EMAIL
#     candidateId: int | None = Field(None, examples=[1])
#
# class Notification(NotificationCreate):       # response
#     id: int
#     status: NotificationStatus
#     createdAt: datetime
