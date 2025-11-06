<<<<<<< HEAD
First automated deployment test.
=======
# selenium-service

Small FastAPI service that runs a Selenium task and returns the result.

## Endpoints
- `GET /healthz` – liveness/monitoring
- `POST /run` – protected, requires `Authorization: Bearer <API_TOKEN>`

## Environment
- `API_TOKEN` must be set (container reads it from the env)
- exposed on `127.0.0.1:8080` via docker-compose
- Caddy fronts it at https://api.simplyhealthchiropractic.com

## Run locally with Docker Compose
```bash
docker compose up -d
```
>>>>>>> aaa346b (Add README documentation)

Updated: testing deploy pipeline

(trigger redeploy)
<!-- trigger deploy -->
