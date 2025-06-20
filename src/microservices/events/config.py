from pydantic_settings import BaseSettings


class Config(BaseSettings):
    KAFKA_HOST: str


config = Config()
