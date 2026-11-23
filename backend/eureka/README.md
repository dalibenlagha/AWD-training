# eureka (discovery server)

Spring Boot 3.5 / Spring Cloud 2025.0 / Java 17. The "phone book" of JobBoard:
every microservice registers here with its **name**, host and port, then sends a heartbeat every 30 s.

## Run
Start it **first**, before the other services.

In IntelliJ: open `EurekaApplication.java` and click Run. Command line (if Maven is installed): `mvn spring-boot:run`

Dashboard: http://localhost:8761 (just after start-up: "No instances available").

## What makes it a Eureka server
| File | Line | Why |
|---|---|---|
| `pom.xml` | `spring-cloud-starter-netflix-eureka-server` | the Eureka server library |
| `pom.xml` | `spring-cloud-dependencies` (BOM) | picks the Spring Cloud versions that match Spring Boot 3.5 |
| `EurekaApplication.java` | `@EnableEurekaServer` | turns the Spring Boot app into a Eureka server |
| `application.properties` | `server.port=8761` | default port of Eureka |
| `application.properties` | `eureka.client.register-with-eureka=false` | the server does not register itself |
| `application.properties` | `eureka.client.fetch-registry=false` | the server does not cache the registry for itself |

## Useful URLs
- Dashboard: http://localhost:8761
- Registry as JSON (the REST API used by the clients): http://localhost:8761/eureka/apps with the header `Accept: application/json`
