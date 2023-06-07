# Whiskey

This project provides a web-deployed API using FastAPI with Uvicorn and Traefik, along with RabbitMQ and Redis with Celery for task processing. The entire application stack is containerized using Docker and orchestrated with Docker Compose. The API requires OAuth access keys for authentication and authorization, and it submits jobs to Celery workers running on a separate virtual machine instance.

## Features

- Web-deployed API using FastAPI and Uvicorn
- Containerized deployment using Docker and Docker Compose
- Task processing with Celery and message queueing with RabbitMQ
- Redis for task result storage and caching
- OAuth access key authentication and authorization
- Scalable architecture with separate Celery workers on virtual machine instances

## Prerequisites

Before running the project, make sure you have the following prerequisites installed:

- Docker: [Install Docker](https://docs.docker.com/get-docker/)
- Docker Compose: [Install Docker Compose](https://docs.docker.com/compose/install/)

## Installation

1. Clone the repository:

   ```shell
   git clone https://github.com/rcorrero/whiskey.git
   ```

2. Navigate to the project directory:

   ```shell
   cd whiskey
   ```

3. Create a `.env` file and provide the necessary environment variables:

   ```plaintext
   # FastAPI and Uvicorn configuration
   FASTAPI_HOST=0.0.0.0
   FASTAPI_PORT=8000

   # RabbitMQ configuration
   RABBITMQ_HOST=rabbitmq
   RABBITMQ_PORT=5672
   RABBITMQ_USERNAME=guest
   RABBITMQ_PASSWORD=guest

   # Redis configuration
   REDIS_HOST=redis
   REDIS_PORT=6379
   REDIS_PASSWORD=

   # OAuth access keys configuration
   OAUTH_CLIENT_ID=
   OAUTH_CLIENT_SECRET=

   # Celery configuration
   CELERY_BROKER_URL=amqp://guest:guest@rabbitmq:5672//
   CELERY_RESULT_BACKEND=redis://:@redis:6379/0

   # Celery worker configuration
   CELERY_WORKER_NAME=worker1
   CELERY_WORKER_CONCURRENCY=4
   ```

4. Build and start the containers:

   ```shell
   docker-compose up --build -d
   ```

5. Access the API at `http://localhost:8000` and make requests using the OAuth access keys.

## Usage

- Use the provided OAuth access keys to authenticate and authorize requests to the API.
- Submit tasks to the API, which will be processed by the Celery workers running on the separate virtual machine instances.
- Monitor task execution and retrieve results using the API.

## Contributing

Contributions are welcome! Here are the steps to contribute to the project:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make your changes and commit them.
4. Push your changes to your forked repository.
5. Submit a pull request to the main repository.

## License

[BSD 3-Clause License](https://opensource.org/license/bsd-3-clause/)

## Contact

For any inquiries or support, please contact [Richard Correro](mailto:richard@richardcorrero.com). Developed by [Richard Correro](mailto:richard@richardcorrero.com).
