# JobSweep Server

Backend server for the JobSweep application.

## Docker Setup

### Prerequisites

- Docker
- Docker Compose

### Running with Docker

1. Build and start the services:

   ```bash
   docker-compose up --build
   ```

2. To run in detached mode:

   ```bash
   docker-compose up -d
   ```

3. To stop the services:
   ```bash
   docker-compose down
   ```

### Environment Variables

Make sure to set up your `.env` file with the following variables:

- `MONGODB_URI` (optional, defaults to mongodb://mongodb:27017/jobsweep)
- `JWT_SECRET_KEY` (required)
- `ENVIRONMENT` (optional, defaults to development)

## Development

To run the server locally without Docker:

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Run the server:
   ```bash
   python app.py
   ```

celery -A services.celery_worker worker --loglevel=info

celery -A services.celery_app.celery beat -S redbeat.RedBeatScheduler

redis-commander --redis-db 1
