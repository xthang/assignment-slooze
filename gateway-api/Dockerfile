# Base Image
FROM python:3.12-slim

RUN apt-get update && apt-get install -y && apt-get install make
RUN pip install --upgrade pip

# set working directory
WORKDIR /app

# add app
COPY . .

COPY ./requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

RUN make prisma-generate

# RUN pytest

# EXPOSE 8000

# start server

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--proxy-headers", "--forwarded-allow-ips", "*"]