# Builds one image that runs the whole Smart Energy website (S1 + S2 + S3 + S4)
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
