const app = require('./app');
const { eurekaClient, PORT } = require('./config/eureka');

app.listen(PORT, () => {
  console.log(`meeting microservice running on http://localhost:${PORT}`);
  console.log(`Swagger UI: http://localhost:${PORT}/swagger-ui`);
  registerInEureka();
});

// ---- Register in Eureka when the application starts ----
// If the Eureka server is not started yet, try again every 10 seconds.
let registered = false;
eurekaClient.on('registered', () => {
  registered = true;
});

function registerInEureka() {
  eurekaClient.start((error) => {
    if (error && !registered) {
      console.warn('Eureka server not reachable, new try in 10 seconds...');
      setTimeout(registerInEureka, 10000);
    }
  });
}

// ---- De-register from Eureka when the application stops ----
// Ctrl+C sends SIGINT. Without this, Eureka keeps showing the instance for about 90 s.
function shutdown(signal) {
  console.log(`${signal} received: de-registering from Eureka...`);
  eurekaClient.stop(() => process.exit(0));
}
process.once('SIGINT', () => shutdown('SIGINT'));
process.once('SIGTERM', () => shutdown('SIGTERM'));
