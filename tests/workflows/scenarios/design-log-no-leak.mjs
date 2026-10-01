import assert from 'node:assert/strict'

// Agent errors that quote the request, the owner proposal and a path must never reach a log line:
// the lines carry the error category and fixed text only (budget, config and transient failures).
const REQUEST = 'CANARY-REQUEST rotate the production api keys'
const PROPOSAL = 'CANARY-PROPOSAL use vendor X for everything'
const PATH = '/home/secret/CANARY-PATH/app.js'
const LEAK = `${REQUEST} | ${PROPOSAL} | ${PATH}`
const KINDS = [
  { name: 'transient', make: () => new Error(`boom: ${LEAK}`) },
  { name: 'budget', make: () => Object.assign(new Error(`over budget: ${LEAK}`), { name: 'WorkflowBudgetExceededError' }) },
  { name: 'config', make: () => new Error(`schema contradiction: ${LEAK}`) },
]
export default {
  argsList: KINDS.map(() => ({ slug: 's', track: 'backend', repo: '/r', tier: 'standard', needsUX: false, investigate: false, request: REQUEST, ownerProposal: PROPOSAL })),
  respond: (_call, state) => { throw KINDS[state.run].make() },
  expect: ({ runs }) => {
    runs.forEach((r, i) => {
      assert.equal(r.error, null, KINDS[i].name)
      assert.ok(r.logs.length > 0, KINDS[i].name)
      assert.ok(!r.logs.some(l => /CANARY/.test(l)), `${KINDS[i].name}: ${JSON.stringify(r.logs)}`)
    })
    assert.equal(runs[1].result.haltedBy, 'budget-cap')
    assert.equal(runs[2].result.haltedBy, 'config-error')
    assert.ok(runs[2].logs.includes('HALT config-error: agent config error'))
  },
}
