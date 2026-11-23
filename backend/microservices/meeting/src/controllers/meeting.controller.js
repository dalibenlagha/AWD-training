/**
 * Meeting controller.
 *
 * Only `hello` is implemented. The meeting logic is a TODO for students (see TODO.md).
 */
const candidatClient = require('../services/candidat.client');

const hello = (req, res) => {
  res.status(200).json({ message: "hello I'm microservice meeting" });
};

// Bonus (Eureka): GET /api/meetings/candidates/:id
// Finds CANDIDAT through Eureka (no hard-coded URL), then calls GET /api/candidates/{id}
const getCandidate = async (req, res) => {
  const { id } = req.params;
  if (!/^\d+$/.test(id)) {
    return res.status(400).json({ status: 400, error: 'Bad Request', message: `Invalid candidate id: ${id}` });
  }
  const { status, body, servedBy } = await candidatClient.getCandidateById(id);
  if (status !== 200) {
    return res.status(status).json(body); // e.g. 404 sent back by candidat
  }
  // servedBy shows which CANDIDAT instance answered (useful with 2 instances: 8081 and 8091)
  res.status(200).json({ servedBy, candidate: body });
};

// TODO (students): implement the Meeting logic.
// No database: keep meetings in memory, for example:
//
// let meetings = [];
// let nextId = 1;
//
// const findAll = (req, res) => { ... };
// const findById = (req, res) => { ... };   // 404 if not found
// const create = (req, res) => { ... };     // 400 if invalid, 201 + created meeting
// const update = (req, res) => { ... };     // 404 / 400 / 200
// const remove = (req, res) => { ... };     // 404 / 204

module.exports = {
  hello,
  getCandidate,
  // TODO (students): export findAll, findById, create, update, remove
};
