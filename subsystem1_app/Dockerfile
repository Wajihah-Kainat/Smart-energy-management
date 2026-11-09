# Builds a small image that runs the Smart Energy app
FROM python:3.12-slim

WORKDIR /code

# install the libraries first (Docker can then reuse this step)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy the application
COPY . .

# the database file lives in /data so it can be kept outside the container
ENV DATABASE=/data/energy.db
VOLUME /data

EXPOSE 5000
CMD ["python", "run.py"]
