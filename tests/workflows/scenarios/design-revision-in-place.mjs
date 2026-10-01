import assert from 'node:assert/strict'

const R = 'addit-harness:'
// Round 1 raises a blocking finding, round 2 is clean: the round-2 architect prompt must be an in-place revision.
export default {
  args: { slug: 's', track: 'backend', repo: '/r', request: 'x', needsUX: false, investigate: false, tier: 'standard' },
  respond: ({ agentType, opts }, state) => {
    if (agentType === `${R}architect-reviewer` && opts.schema) {
      state.reviews = (state.reviews ?? 0) + 1
      return { findings: state.reviews === 1 ? [{ severity: 'blocking', description: 'F1 missing rollback' }] : [] }
    }
    return 'text'
  },
  expect: out => {
    assert.equal(out.error, null)
    assert.equal(out.result.designRounds, 2)
    const designs = out.callList.filter(c => c.agentType === `${R}backend-architect` && c.opts.phase === 'Design')
    assert.equal(designs.length, 2)
    assert.doesNotMatch(designs[0].prompt, /IN PLACE/)
    assert.match(designs[1].prompt, /edit \/r\/docs\/work\/s\/solutions\/solution-backend\.md IN PLACE per doc-protocol\.md/)
    assert.match(designs[1].prompt, /F1 missing rollback/)
    assert.doesNotMatch(designs[1].prompt, /address each/)
    const plan = out.callList.find(c => c.opts.phase === 'Plan' && c.agentType === `${R}backend-architect`)
    assert.doesNotMatch(plan.prompt, /ADR candidates/)
  },
}
