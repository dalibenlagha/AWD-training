/**
 * Eureka client of the meeting microservice (library: eureka-js-client).
 *
 * Eureka is the "phone book" of the microservices. With this client, Meeting:
 *  1. registers itself under the name MEETING at start-up   -> POST   /eureka/apps/MEETING
 *  2. sends a heartbeat every 30 s ("I am still alive")      -> PUT    /eureka/apps/MEETING/{instanceId}
 *  3. downloads the registry every 30 s (local cache)        -> GET    /eureka/apps
 *  4. de-registers itself when the application stops         -> DELETE /eureka/apps/MEETING/{instanceId}
 *
 * The client is only CREATED here. It is started in server.js (not in app.js),
 * so the tests can use the Express app without a Eureka server.
 */
const { Eureka } = require('eureka-js-client');

// Read the port from the environment, so several instances can run at the same time:
//   PowerShell:  $env:PORT=8093; npm start        Linux / macOS:  PORT=8093 npm start
const PORT = Number(process.env.PORT) || 8083;

// Where is the Eureka server? (change it only if Eureka runs on another computer)
const EUREKA_HOST = process.env.EUREKA_HOST || 'localhost';
const EUREKA_PORT = Number(process.env.EUREKA_PORT) || 8761;

const HOST = 'localhost';
const IP_ADDRESS = '127.0.0.1';

const eurekaClient = new Eureka({
  // ---- Who am I? (this instance) ----
  instance: {
    app: 'MEETING', // name shown in the Eureka dashboard
    instanceId: `${HOST}:meeting:${PORT}`, // unique id: 2 instances = 2 different ports, so both are visible
    hostName: HOST, // host of this instance
    ipAddr: IP_ADDRESS, // IP address of this instance
    port: { $: PORT, '@enabled': true }, // Eureka expects exactly this format for the port
    vipAddress: 'meeting', // logical name that other services can use to find Meeting
    statusPageUrl: `http://${HOST}:${PORT}/health`, // Bonus: link opened from the dashboard
    healthCheckUrl: `http://${HOST}:${PORT}/health`, // Bonus: URL that tells if the instance is healthy
    dataCenterInfo: {
      '@class': 'com.netflix.appinfo.InstanceInfo$DefaultDataCenterInfo',
      name: 'MyOwn', // "MyOwn" = our own machine (not Amazon AWS)
    },
  },
  // ---- Where is the Eureka server? ----
  eureka: {
    host: EUREKA_HOST,
    port: EUREKA_PORT,
    servicePath: '/eureka/apps/', // REST path of the Spring Eureka server
  },
});

module.exports = { eurekaClient, PORT };
