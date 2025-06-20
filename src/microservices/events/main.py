import asyncio
import datetime
import json
import logging
import uuid

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer, ConsumerRecord
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from config import config
from schemas import MoviesEventSchema, PaymentsEventSchema, UsersEventSchema

logging.getLogger().setLevel(logging.INFO)

app = FastAPI(title="Events")


class ReverseProxyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        try:
            return await call_next(request)
        except Exception as e:
            logging.exception(e)
            return JSONResponse(content={"error": "Internal Server Error"})


app.add_middleware(ReverseProxyMiddleware)


async def process_event[T](event: T) -> None:
    type_topic_dict = {
        MoviesEventSchema: "movie-events",
        UsersEventSchema: "user-events",
        PaymentsEventSchema: "payment-events",
    }
    producer = AIOKafkaProducer(
        bootstrap_servers=config.KAFKA_HOST,
        compression_type="gzip",
    )
    consumer = AIOKafkaConsumer(
        type_topic_dict.get(type(event)),
        bootstrap_servers=config.KAFKA_HOST,
        auto_offset_reset="latest",
        group_id=f"temp-group-{uuid.uuid4()}",
        enable_auto_commit=True,
    )
    await consumer.start()
    await producer.start()
    await producer.send(
        type_topic_dict.get(type(event)),
        event.model_dump_json().encode(),
    )
    await producer.stop()
    kafka_event: ConsumerRecord = await asyncio.wait_for(consumer.getone(), timeout=2.0)
    await consumer.stop()
    return {
        "status": "success",
        "partition": kafka_event.partition,
        "offset": kafka_event.offset,
        "event": {
            "id": uuid.uuid4(),
            "type": type_topic_dict.get(type(event)).split("-")[0],
            "timestamp": datetime.datetime.fromtimestamp(
                kafka_event.timestamp / 1000
            ).isoformat(),
            "payload": json.loads(kafka_event.value),
        },
    }


#
@app.post("/api/events/movie")
async def create_movie_event(event: MoviesEventSchema) -> None:
    return await process_event(event=event)


@app.post("/api/events/user")
async def create_user_event(event: UsersEventSchema) -> None:
    return await process_event(event=event)


@app.post("/api/events/payment")
async def create_payment_event(event: PaymentsEventSchema) -> None:
    return await process_event(event=event)
