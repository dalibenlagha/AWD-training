// Tests of the Eureka bonus (GET /health and GET /api/meetings/candidates/:id).
// No Eureka server is needed: the registry cache of the client is filled by hand,
// exactly as if Eureka had answered GET /eureka/apps.
const { test, before, after, beforeEach } = require('node:test');
const assert = require('node:assert/strict');
const http = require('node:http');
const app = require('../src/app');
const { eurekaClient } = require('../src/config/eureka');

let server;
let baseUrl;
let fakeCandidat; // a tiny HTTP server that plays the role of the candidat microservice
let fakeCandidatPort;

before(async () => {
  server = app.listen(0);
  await new Promise((resolve) => server.once('listening', resolve));
  baseUrl = `http://localhost:${server.address().port}`;

  fakeCandidat = http.createServer((req, res) => {
    res.setHeader('Content-Type', 'application/json');
    if (req.url === '/api/candidates/1') {
      res.end(JSON.stringify({ id: 1, firstname: 'Badia', lastname: 'Abouhdid' }));
    } else {
      res.statusCode = 404;
      res.end(JSON.stringify({ status: 404, detail: 'Candidate not found' }));
    }
  });
  fakeCandidat.listen(0);
  await new Promise((resolve) => fakeCandidat.once('listening', resolve));
  fakeCandidatPort = fakeCandidat.address().port;
});

after(() => {
  server.close();
  fakeCandidat.close();
});

// Empty registry before each test
beforeEach(() => eurekaClient.transformRegistry({ applications: { application: [] } }));

function registerFakeCandidat() {
  eurekaClient.transformRegistry({
    applications: {
      application: [{
        name: 'CANDIDAT',
        instance: [{
          instanceId: `test:candidat:${fakeCandidatPort}`,
          app: 'CANDIDAT',
          hostName: 'localhost',
          ipAddr: '127.0.0.1',
          status: 'UP',
          port: { $: fakeCandidatPort, '@enabled': 'true' },
          vipAddress: 'candidat',
        }],
      }],
    },
  });
}

test('GET /health returns UP', async () => {
  const res = await fetch(`${baseUrl}/health`);
  assert.equal(res.status, 200);
  assert.deepEqual(await res.json(), { status: 'UP' });
});

test('GET /api/meetings/candidates/abc returns 400', async () => {
  const res = await fetch(`${baseUrl}/api/meetings/candidates/abc`);
  assert.equal(res.status, 400);
});

test('no CANDIDAT in Eureka: 503', async () => {
  const res = await fetch(`${baseUrl}/api/meetings/candidates/1`);
  assert.equal(res.status, 503);
  assert.match((await res.json()).message, /CANDIDAT/);
});

test('CANDIDAT found through Eureka: the candidate is returned with the instance that answered', async () => {
  registerFakeCandidat();
  const res = await fetch(`${baseUrl}/api/meetings/candidates/1`);
  assert.equal(res.status, 200);
  const body = await res.json();
  assert.equal(body.servedBy, `http://127.0.0.1:${fakeCandidatPort}`);
  assert.equal(body.candidate.id, 1);
});

test('unknown candidate: the 404 of candidat is sent back', async () => {
  registerFakeCandidat();
  const res = await fetch(`${baseUrl}/api/meetings/candidates/2`);
  assert.equal(res.status, 404);
});
