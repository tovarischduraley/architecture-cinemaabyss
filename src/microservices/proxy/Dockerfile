FROM python:3.13-slim


WORKDIR /app

COPY pyproject.toml main.py ./

RUN pip install --root-user-action ignore uv
RUN uv sync --no-dev --compile-bytecode

CMD [ "uv", "run",  "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
