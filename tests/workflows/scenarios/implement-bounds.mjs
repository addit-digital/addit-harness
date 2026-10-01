import assert from 'node:assert/strict'

// Adversarial stubs: reviewers never clean (fresh blocking findings each call, so the breaker never trips),
// QA always fails, all five reviewers present. Every run must hit the worst-case cell EXACTLY.
const R = 'addit-harness:'
const SHA = 'a'.repeat(64)
const CASES = ['light', 'standard', 'deep'].flatMap(tier => [
  { tier, track: 'backend' },
  { tier, track: 'both' }, // same repo: developers run sequentially
  { tier, track: 'both', secondaryRepo: '/r2' }, // separate repos: developers run in parallel
])
// implement + review passes (light: code-reviewer x3; else 5+5+1) + fix rounds (2 x developers)
// + QA + post-QA fix + [standard/deep: scoped re-review] + QA re-verify
const worst = ({ tier, track }) => {
  const devs = track === 'both' ? 2 : 1
  const reviews = tier === 'light' ? 3 : 11
  return devs + reviews + 2 * devs + 1 + devs + (tier === 'light' ? 0 : 1) + 1
}
let n = 0
export default {
  argsList: CASES.map(c => ({ slug: 's', track: c.track, repo: '/r', secondaryRepo: c.secondaryRepo, planSha256: SHA, tier: c.tier, plannedFiles: ['a.js'] })),
  respond: ({ agentType }) => {
    if (agentType === `${R}qa-engineer`) return { passed: false, findings: ['broken'], evidence: [] }
    if (agentType.endsWith('code-reviewer') || agentType.startsWith('pr-review-toolkit:'))
      return { findings: [{ severity: 'blocking', description: `f${n++}` }], touchedFiles: ['a.js'] }
    return 'done'
  },
  expect: ({ runs }) => {
    CASES.forEach((c, i) => {
      const r = runs[i], name = JSON.stringify(c)
      assert.equal(r.error, null, name)
      assert.equal(r.result.haltedBy, null, name) // never 'call-ceiling'; no scope breach inside the plan
      assert.equal(r.result.qaRuns, 2, name)
      assert.equal(r.result.reviewRounds, 3, name)
      assert.equal(r.calls, worst(c), name)
    })
    assert.deepEqual(runs.map(r => r.calls), [9, 13, 13, 18, 22, 22, 18, 22, 22])
  },
}
