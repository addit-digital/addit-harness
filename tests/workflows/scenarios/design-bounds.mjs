import assert from 'node:assert/strict'

// Adversarial stubs: every reviewer returns fresh blocking findings (the breaker never trips, nothing is ever
// approved), figma always builds, investigation is on. Every run must hit the worst-case cell EXACTLY.
const R = 'addit-harness:'
const TIERS = ['light', 'standard', 'deep']
const CASES = TIERS.flatMap(tier => ['backend', 'both'].flatMap(track => [false, true].map(needsUX => ({ tier, track, needsUX }))))
// light: [1 brief | 2 briefs + write] + 1 review; no UX, no investigate. standard/deep: investigate 1 + UX 3x3 + 3 rounds x (tracks + 1 review) + plan + plan review.
const worst = ({ tier, track, needsUX }) => tier === 'light'
  ? (track === 'both' ? 4 : 2)
  : 1 + (needsUX ? 9 : 0) + 3 * ((track === 'both' ? 2 : 1) + 1) + 2
let n = 0
export default {
  argsList: CASES.map(c => ({ slug: 's', track: c.track, repo: '/r', request: 'x', needsUX: c.needsUX, investigate: true, tier: c.tier })),
  respond: ({ agentType, opts }) => {
    if (agentType === `${R}figma-designer`) return { fileUrl: 'u', nodeIds: [], designDefectsFound: [] }
    if (opts.schema) return { findings: [{ severity: 'blocking', description: `f${n++}` }] }
    return 'text'
  },
  expect: ({ runs }) => {
    CASES.forEach((c, i) => {
      const r = runs[i], name = JSON.stringify(c)
      assert.equal(r.error, null, name)
      assert.notEqual(r.result.haltedBy, 'call-ceiling', name)
      assert.equal(r.result.haltedBy, null, name)
      assert.equal(r.calls, worst(c), name)
    })
  },
}
