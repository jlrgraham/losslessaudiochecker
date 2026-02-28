FROM python:3-slim

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install flask redis

COPY app.py /app.py

EXPOSE 5000

CMD ["python", "/app.py"]
