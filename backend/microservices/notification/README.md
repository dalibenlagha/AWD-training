# notification microservice

Python / FastAPI microservice, **no database**, with Swagger documentation generated automatically.
It exposes one endpoint for now; the notification logic is a TODO for students (see [TODO.md](TODO.md)).

## Run
```bash
cd chemin\vers\notification

# 1. Créer et activer l'environnement virtuel (une seule fois)
python -m venv venv
.\venv\Scripts\Activate.ps1

# 2. Installer les dépendances
python -m pip install -r requirements.txt

# 3. Lancer le microservice
python -m uvicorn app.main:app --reload --port 8084   # or: python -m app.main
```
- API: http://localhost:8084/api/notifications/hello
- Swagger UI: http://localhost:8084/swagger-ui
- OpenAPI JSON: http://localhost:8084/v3/api-docs
- ReDoc: http://localhost:8084/redoc

Port `8084` (candidat = 8081, job = 8082, meeting = 8083).

## Endpoint
| Method | Path | Response |
|---|---|---|
| GET | /api/notifications/hello | `200 {"message": "hello I'm microservice notification"}` |

## Eureka (workshop, Chapter 4)
When FastAPI starts (the *lifespan* in `app/main.py`), the service registers in Eureka as **NOTIFICATION**
(`app/eureka.py`), sends a heartbeat every 30 s, and de-registers when it stops (Ctrl+C).
Start the Eureka server (port 8761) first. If Eureka is not started yet, you see
`Register error! Will try in next heartbeat`: it tries again every 30 s.

**The port given to Eureka must be the port uvicorn listens on.** Both come from the `PORT` variable, so the
simplest is `python -m app.main`:
```bash
python -m app.main                       # instance 1: port 8084
$env:PORT=8094; python -m app.main       # instance 2, another terminal (Windows PowerShell)
PORT=8094 python -m app.main             # instance 2 (Linux / macOS)
```
With the uvicorn command, give the same port twice: `$env:PORT=8094; python -m uvicorn app.main:app --port 8094`.

| Variable | Default | Role |
|---|---|---|
| `PORT` | 8084 | port of this instance (also the port given to Eureka) |
| `EUREKA_SERVER` | http://localhost:8761/eureka | URL of the Eureka server |

Bonus endpoints:
| Method | Path | Response |
|---|---|---|
| GET | /health | `200 {"status": "UP"}`, declared to Eureka as `healthCheckUrl` and `statusPageUrl` |
| GET | /api/notifications/candidates/{id} | finds CANDIDAT through Eureka, then calls its `GET /api/candidates/{id}`: `200 {"servedBy": "http://...:8081", "candidate": {...}}`, 404 from candidat, 503 if no CANDIDAT instance |

## Tests
```bash
pip install -r requirements-dev.txt
pytest
```

## Structure
```
notification/
├── app/
│   ├── main.py                    FastAPI app + Swagger config, lifespan (Eureka), /health
│   ├── eureka.py                  Eureka client (name NOTIFICATION, host, port, Eureka server)
│   ├── schemas.py                 Pydantic models (validation + Swagger schemas)
│   └── routers/notification.py    /api/notifications routes (hello, candidate via Eureka + TODO)
├── tests/test_hello.py
├── tests/test_eureka.py           tests of /health and of the call to CANDIDAT (no Eureka needed)
├── TODO.md                        work for students
├── requirements.txt / requirements-dev.txt
└── pytest.ini
```
