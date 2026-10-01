import assert from 'node:assert/strict'

// Worst cases with the owner idea in play: every review blocking forever, figma always builds, investigation on.
// standard: +1 owner-idea call per track. deep: +3 explorers, the other track's owner-idea call, and (once) a candidate switch.
// Both must land on the cap exactly and never halt on call-ceiling.
const R = 'addit-harness:'
const isExplorer = c => /role: explorer/.test(c.prompt)
const CASES = [
  { tier: 'standard', track: 'both', needsUX: true, cap: 23 },
  { tier: 'deep', track: 'both', needsUX: true, cap: 27 },
  { tier: 'deep', track: 'backend', needsUX: true, cap: 23 },
]
let n = 0
export default {
  argsList: CASES.map(c => ({
    slug: 'abc', track: c.track, repo: '/r', secondaryRepo: '/f', request: 'x', needsUX: c.needsUX, investigate: true, tier: c.tier,
    fanoutTrack: 'backend', ownerProposal: 'idea',
  })),
  respond: (call, state) => {
    if (call.agentType === `${R}figma-designer`) return { fileUrl: 'u', nodeIds: [], designDefectsFound: [] }
    if (isExplorer(call)) return { summary: 's', priorArt: [], preMortem: [], typicality: 0.5 }
    if (call.opts.schema) {
      const first = call.opts.phase === 'Design' && !state.altSent // only the first design review proposes an alternative
      if (first) state.altSent = true
      return { findings: [{ severity: 'blocking', description: `f${n++}` }], ...(first ? { betterAlternative: { candidate: 'Y', rationale: 'r' } } : {}) }
    }
    return 'text'
  },
  expect: ({ runs }) => {
    CASES.forEach((c, i) => {
      const r = runs[i], name = JSON.stringify(c)
      assert.equal(r.error, null, name)
      assert.equal(r.result.haltedBy, null, name)
      assert.equal(r.calls, c.cap, name)
    })
  },
}
