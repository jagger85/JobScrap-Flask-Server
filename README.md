# JobScrap Flask Server 🤖

[![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-000000?style=flat&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Celery](https://img.shields.io/badge/Celery-37814A?style=flat&logo=celery&logoColor=white)](https://docs.celeryproject.org/)
[![Redis](https://img.shields.io/badge/Redis-DC382D?style=flat&logo=redis&logoColor=white)](https://redis.io/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)

## Overview 🎯
This is the server component of the JobScrap application. It handles job data processing and scheduling tasks using Celery with Redis as the message broker. The entire application is containerized using Docker for easy deployment and scaling.

## Architecture 🏗️

The application consists of several containerized services:

- **Flask App** 🌶️: Main application server (Port: 5000)
- **Redis** 📦: Message broker and data storage (Port: 6379)
- **Redis Commander** 🔍: Redis management UI (Port: 8081)
- **Celery Worker** 👷: Task processing
- **Celery Beat** ⏰: Task scheduling with RedBeat

## Prerequisites 📋

- Docker
- Docker Compose
- `.env` file with required environment variables

## Environment Variables 🔐

Create a `.env` file in the root directory with the following variables:

```bash
MONGODB_URI=your_mongodb_uri
JWT_SECRET_KEY=your_secret_key
ENVIRONMENT=development
REDIS_HOST=redis
REDIS_PORT=6379
```

## Installation and Setup 📥

1. Clone the repository:
```bash
git clone <repository-url>
cd JobScrap-Flask-Server
```

2. Create and configure your `.env` file as described above

3. Build and start the containers:
```bash
docker-compose up --build
```

This will start all services:
- Flask app on http://localhost:5000
- Redis Commander on http://localhost:8081
- Redis on port 6379

## Development 🚀

### Service Commands

All services are managed through Docker Compose. Here are the main commands:

```bash
# Start all services
docker-compose up

# Start services in detached mode
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f

# View logs for specific service
docker-compose logs -f [service_name]
```

### Service-Specific Information

#### Celery Worker
```bash
# Inside the container
celery -A services.celery_worker worker --loglevel=info
```

#### Celery Beat with RedBeat Scheduler
```bash
# Inside the container
celery -A services.celery_app.celery beat -S redbeat.RedBeatScheduler
```

#### Redis Commander
Access the Redis management interface at http://localhost:8081

## Networks and Volumes 🌐

- **Network**: All services are connected through the `jobsweep-network`
- **Volumes**: Redis data is persisted through the `redis_data` volume

## Documentation 📚

For more detailed information about the API endpoints and available features, please refer to the API documentation when the server is running.