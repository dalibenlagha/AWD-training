/**
 * Bonus: call the candidat microservice WITHOUT writing its URL in the code.
 *
 *  1. Ask the Eureka client for the instances of CANDIDAT.
 *     The answer comes from the local cache of the registry (refreshed every 30 s), not from a new request.
 *  2. Pick one instance at random: a very simple load balancing between 8081, 8091...
 *  3. Call http://<ip>:<port>/api/candidates/{id} on that instance.
 */
const { eurekaClient } = require('../config/eureka');

function httpError(status, message) {
  const error = new Error(message);
  error.status = status;
  return error;
}

// Steps 1 and 2: find the address of one CANDIDAT instance in Eureka
function findCandidatUrl() {
  const instances = eurekaClient.getInstancesByAppId('CANDIDAT'); // only the instances with status UP
  if (instances.length === 0) {
    throw httpError(503, 'No instance of CANDIDAT is registered in Eureka');
  }
  const instance = instances[Math.floor(Math.random() * instances.length)];
  return `http://${instance.ipAddr}:${instance.port.$}`;
}

// Step 3: call GET /api/candidates/{id} on that instance
async function getCandidateById(id) {
  const baseUrl = findCandidatUrl();

  let response;
  try {
    // short timeout: never wait forever for another service
    response = await fetch(`${baseUrl}/api/candidates/${id}`, { signal: AbortSignal.timeout(5000) });
  } catch {
    throw httpError(503, `CANDIDAT instance ${baseUrl} is not reachable`);
  }

  const text = await response.text();
  let body;
  try {
    body = JSON.parse(text);
  } catch {
    body = { message: text };
  }
  return { status: response.status, body, servedBy: baseUrl };
}

module.exports = { getCandidateById };
