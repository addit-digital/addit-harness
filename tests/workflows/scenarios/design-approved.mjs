import assert from 'node:assert/strict'

const R = 'addit-harness:'
export default {
  args: { slug: 's', track: 'backend', repo: '/r', request: 'x', needsUX: false, investigate: false, tier: 'standard' },
  respond: ({ agentType, opts }) => {
    if (agentType === `${R}architect-reviewer` && opts.schema) return { findings: [] }
    return 'text'
  },
  expect: out => {
    assert.equal(out.error, null)
    assert.equal(out.result.designApproved, true)
    assert.equal(out.result.planWritten, true)
    assert.equal(out.result.designRounds, 1)
    assert.deepEqual(out.phases, ['Investigate', 'Design', 'Plan'])
    assert.equal(out.result.tier, 'standard')
    assert.deepEqual(out.result.tracksCompleted, ['backend'])
    assert.equal(out.calls, 4) // design + review + plan + plan review: the writer call is merged away
    assert.equal(out.result.planApproved, true)
  },
}
