"""Eureka client of the notification microservice (library: py-eureka-client).

Eureka is the "phone book" of the microservices. With this client, Notification:
 1. registers itself under the name NOTIFICATION at start-up  -> POST   /eureka/apps/NOTIFICATION
 2. sends a heartbeat every 30 s ("I am still alive")         -> PUT    /eureka/apps/NOTIFICATION/{instanceId}
 3. downloads the registry every 30 s (local cache)           -> GET    /eureka/apps
 4. de-registers itself when the application stops            -> DELETE /eureka/apps/NOTIFICATION/{instanceId}

start_eureka() and stop_eureka() are called by the FastAPI lifespan (see main.py).
If the Eureka server is not started yet, the client tries again at the next heartbeat (30 s).
"""
import os
import random

import py_eureka_client.eureka_client as eureka_client

# Read the port from the environment, so several instances can run at the same time.
# It MUST be the port uvicorn really listens on:
#   PowerShell:  $env:PORT=8094; python -m app.main
PORT = int(os.getenv("PORT", "8084"))

# Where is the Eureka server? (change it only if Eureka runs on another computer)
EUREKA_SERVER = os.getenv("EUREKA_SERVER", "http://localhost:8761/eureka")

HOST = "localhost"
IP_ADDRESS = "127.0.0.1"


async def start_eureka() -> None:
    """Register in Eureka (called when FastAPI starts)."""
    await eureka_client.init_async(
        eureka_server=EUREKA_SERVER,                 # where is the Eureka server?
        app_name="NOTIFICATION",                     # name shown in the Eureka dashboard
        instance_id=f"{HOST}:notification:{PORT}",   # unique id: 2 instances = 2 different ports
        instance_host=HOST,                          # host of this instance
        instance_ip=IP_ADDRESS,                      # IP address of this instance
        instance_port=PORT,                          # same port as uvicorn
        health_check_url=f"http://{HOST}:{PORT}/health",  # Bonus: URL that tells if the instance is healthy
        status_page_url=f"http://{HOST}:{PORT}/health",   # Bonus: link opened from the dashboard
    )


async def stop_eureka() -> None:
    """De-register from Eureka (called when FastAPI stops, e.g. Ctrl+C)."""
    await eureka_client.stop_async()


def find_service_url(app_name: str) -> str | None:
    """Bonus: find the address of one UP instance of `app_name`, without any hard-coded URL.

    The answer comes from the local copy of the registry (refreshed every 30 s).
    With several instances, one is chosen at random: a very simple load balancing.
    """
    client = eureka_client.get_client()
    if client is None or client.applications is None:  # Eureka client not started / registry not loaded yet
        return None
    instances = client.applications.get_application(app_name).up_instances
    if not instances:
        return None
    instance = random.choice(instances)
    return f"http://{instance.ipAddr}:{instance.port.port}"
