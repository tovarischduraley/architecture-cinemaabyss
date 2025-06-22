import datetime

from pydantic import BaseModel


class MoviesEventSchema(BaseModel):
    movie_id: int | None = None
    title: str | None = None
    action: str | None = None
    user_id: int | None = None
    rating: float | None = None
    genres: list | None = None
    description: str | None = None


class UsersEventSchema(BaseModel):
    username: str | None = None
    user_id: int | None = None
    email: str | None = None
    timestamp: datetime.datetime | None = None
    action: str | None = None


class PaymentsEventSchema(BaseModel):
    payment_id: int | None = None
    user_id: int | None = None
    status: str | None = None
    amount: float | None = None
    timestamp: datetime.datetime | None = None
    method_type: str | None = None
