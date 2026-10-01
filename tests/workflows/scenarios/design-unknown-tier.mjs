import assert from 'node:assert/strict'

const R = 'addit-harness:'
export default {
  args: { slug: 's', track: 'backend', repo: '/r', request: 'x', needsUX: false, investigate: false, tier: 'bogus' },
  respond: ({ agentType, opts }) => (agentType === `${R}architect-reviewer` && opts.schema ? { findings: [] } : 'text'),
  expect: out => {
    assert.equal(out.result.tier, 'standard')
    assert.ok(out.logs.includes("tier 'bogus' unrecognised — standard"))
    assert.equal(out.calls, 4)
  },
}
