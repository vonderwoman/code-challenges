# Use the official Python image.
# https://hub.docker.com/_/python
FROM --platform=linux/amd64 python:3.11-slim@sha256:5a67c38a7c28ad09d08f4e153280023a2df77189b55af7804d7ceb96fee6a68f

# https://cloud.google.com/run/docs/reference/container-contract#port
ENV PORT=8000

ENV APP_HOME /app
WORKDIR $APP_HOME

# install deps
COPY requirements.txt constraints.txt ./
RUN python -m venv venv && \
    ./venv/bin/pip install -c constraints.txt --upgrade pip wheel setuptools --no-cache-dir && \
    ./venv/bin/pip install -r requirements.txt --no-cache-dir

# copy app
COPY . ./

# copy data
COPY --from=api-backend prices.csv ./

# Run the web service on container startup.
# https://www.uvicorn.org/deployment
CMD . venv/bin/activate && exec gunicorn --bind :$PORT -k uvicorn.workers.UvicornWorker main:app
