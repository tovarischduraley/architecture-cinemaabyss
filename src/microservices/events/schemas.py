import datetime

from pydantic import BaseModel


class MoviesEventSchema(BaseModel):
    movie_id: int
    title: str
    action: str
    user_id: int
    rating: float
    genres: list
    description: str


class UsersEventSchema(BaseModel):
    username: str
    user_id: int
    email: str
    timestamp: datetime.datetime
    action: str


class PaymentsEventSchema(BaseModel):
    payment_id: int
    user_id: int
    status: str
    amount: float
    timestamp: datetime.datetime
    method_type: str
