import assert from 'node:assert/strict'

const R = 'addit-harness:'
const base = { slug: 's', track: 'backend', repo: '/r', request: 'x', needsUX: false, investigate: true, tier: 'standard' }
// With briefPath the in-workflow investigator is skipped and every prompt points at the brief;
// without it the investigator runs and no brief line appears.
export default {
  argsList: [{ ...base, briefPath: '/r/docs/work/s/specs/brief.md' }, base],
  respond: ({ agentType, opts }) => {
    if (agentType === `${R}architect-reviewer` && opts.schema) return { findings: [] }
    return 'text'
  },
  expect: ({ runs: [withBrief, without] }) => {
    assert.equal(withBrief.error, null)
    assert.equal(withBrief.callsByType[`${R}product-owner`], undefined)
    assert.equal(withBrief.calls, 4)
    for (const c of withBrief.callList) assert.match(c.prompt, /Problem brief \(supersedes the raw request; read first\): \/r\/docs\/work\/s\/specs\/brief\.md/)
    assert.equal(without.callsByType[`${R}product-owner`], 1)
    assert.equal(without.calls, 5)
    for (const c of without.callList) assert.doesNotMatch(c.prompt, /Problem brief/)
  },
}
