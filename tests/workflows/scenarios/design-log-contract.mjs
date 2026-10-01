import assert from 'node:assert/strict'

// Standard tier, one failing design review then a clean one: pins every progress-view line and the no-leak rule.
const R = 'addit-harness:'
const REQUEST = 'SENTINEL-REQUEST-TEXT please rotate the api keys'
let reviews = 0
export default {
  args: { slug: 's', track: 'backend', repo: '/r', request: REQUEST, needsUX: false, investigate: false, tier: 'standard' },
  respond: ({ agentType, opts }) => {
    if (agentType === `${R}architect-reviewer` && opts.schema) {
      reviews++
      return { findings: reviews === 1 ? [{ severity: 'blocking', description: 'SENTINEL-AGENT-OUTPUT' }, { severity: 'minor', description: 'nit' }] : [] }
    }
    return 'text'
  },
  expect: out => {
    assert.equal(out.error, null)
    assert.deepEqual(out.logs, [
      'dev-flow design start: tier=standard track=backend',
      'Design r1/3: 1 blocking',
      'Design r2/3: 0 blocking',
      'Plan r1/1: 0 blocking',
      'gate design_review: pass',
    ])
    assert.ok(!out.logs.some(l => /SENTINEL/.test(l)))
  },
}
