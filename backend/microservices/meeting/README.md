# meeting microservice

Node.js / Express microservice, **no database**, documented with Swagger (OpenAPI 3).
It exposes one endpoint for now; the meeting logic is a TODO for students (see [TODO.md](TODO.md)).

## Run
```bash
npm install
npm start          # or: npm run dev  (auto-restart on changes)
```
- API: http://localhost:8083/api/meetings/hello
- Swagger UI: http://localhost:8083/swagger-ui
- OpenAPI JSON: http://localhost:8083/v3/api-docs

Port: `8083` by default (candidat = 8081, job = 8082). Change with `PORT=9000 npm start`.

## Endpoint
| Method | Path | Response |
|---|---|---|
| GET | /api/meetings/hello | `200 {"message": "hello I'm microservice meeting"}` |

## Eureka (workshop, Chapter 4)
At start-up the service registers in Eureka as **MEETING** (`src/config/eureka.js`), sends a heartbeat every 30 s,
and de-registers when you press Ctrl+C (`src/server.js`). Start the Eureka server (port 8761) first.
If Eureka is not started yet, you see `ECONNREFUSED 127.0.0.1:8761` and Meeting tries again every 10 s.

2nd instance, in another terminal:
```bash
$env:PORT=8093; npm start      # Windows PowerShell
PORT=8093 npm start            # Linux / macOS
```

| Variable | Default | Role |
|---|---|---|
| `PORT` | 8083 | port of this instance (also the port given to Eureka) |
| `EUREKA_HOST` | localhost | host of the Eureka server |
| `EUREKA_PORT` | 8761 | port of the Eureka server |

Bonus endpoints:
| Method | Path | Response |
|---|---|---|
| GET | /health | `200 {"status": "UP"}`, declared to Eureka as `healthCheckUrl` and `statusPageUrl` |
| GET | /api/meetings/candidates/{id} | finds CANDIDAT through Eureka, then calls its `GET /api/candidates/{id}`: `200 {"servedBy": "http://...:8081", "candidate": {...}}`, 404 from candidat, 503 if no CANDIDAT instance |

`npm install` prints warnings about `request` (deprecated, vulnerabilities): it is an old library used inside
`eureka-js-client`. This is expected for the workshop; do not run `npm audit fix --force`.

## Tests
```bash
npm test
```
Uses Node's built-in test runner (`node:test`), Node 18+.

## Structure
```
meeting/
├── src/
│   ├── server.js                      starts the HTTP server, registers in Eureka, de-registers on Ctrl+C
│   ├── app.js                         Express app: JSON, Swagger, /health, routes, 404, errors
│   ├── config/eureka.js               Eureka client (name MEETING, host, port, Eureka server)
│   ├── config/swagger.js              OpenAPI spec (document new routes here)
│   ├── routes/meeting.routes.js       URL -> controller mapping
│   ├── controllers/meeting.controller.js   request handling (hello, candidate via Eureka + TODO)
│   └── services/candidat.client.js    finds CANDIDAT in Eureka and calls it
├── test/hello.test.js
├── test/eureka.test.js                tests of /health and of the call to CANDIDAT (no Eureka needed)
├── TODO.md                            work for students
└── package.json
```
