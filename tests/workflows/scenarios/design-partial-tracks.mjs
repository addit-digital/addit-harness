import assert from 'node:assert/strict'

const R = 'addit-harness:'
export default {
  args: { slug: 's', track: 'both', repo: '/r', request: 'x', needsUX: false, investigate: false, tier: 'standard' },
  respond: ({ agentType, opts }) => {
    if (agentType === `${R}frontend-architect`) return null
    if (agentType === `${R}architect-reviewer` && opts.schema) return { findings: [] }
    return 'text'
  },
  expect: out => {
    assert.deepEqual(out.result.tracksCompleted, ['backend'])
    const plan = out.callList.find(c => /Write the implementation plan/.test(c.prompt))
    assert.match(plan.prompt, /solution-backend\.md/)
    assert.doesNotMatch(plan.prompt, /solution-frontend\.md/) // only tracks whose design returned
    assert.equal(out.result.planWritten, true)
  },
}
