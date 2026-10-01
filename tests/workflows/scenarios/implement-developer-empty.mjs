import assert from 'node:assert/strict'

const R = 'addit-harness:'
const base = { slug: 's', planSha256: 'a'.repeat(64), tier: 'standard', repo: '/r' }
// A developer that returns nothing means the plan was not (fully) implemented: the run must halt before review,
// never review an empty diff and report clean / qaPassed.
const CASES = [
  { name: 'single track, developer returns nothing', args: { track: 'backend' }, empty: [`${R}backend-developer`] },
  { name: 'both tracks, frontend returns nothing', args: { track: 'both' }, empty: [`${R}frontend-developer`] },
]
export default {
  argsList: CASES.map(c => ({ ...base, ...c.args })),
  respond: ({ agentType }, state) => {
    if (CASES[state.run].empty.includes(agentType)) return null
    if (agentType === `${R}qa-engineer`) return { passed: true, findings: [], evidence: [] }
    if (agentType.endsWith('code-reviewer')) return { findings: [], touchedFiles: [] }
    if (agentType.startsWith('pr-review-toolkit:')) throw new Error('unknown agent type')
    return 'done'
  },
  expect: ({ runs }) => {
    CASES.forEach((c, i) => {
      const r = runs[i]
      assert.equal(r.error, null, c.name)
      assert.equal(r.result.implementSucceeded, false, c.name)
      assert.equal(r.result.haltedBy, 'implement-failed', c.name)
      assert.equal(r.result.clean, false, c.name)
      assert.equal(r.result.qaPassed, false, c.name)
      assert.equal(r.callsByType[`${R}code-reviewer`] ?? 0, 0, c.name)
      assert.equal(r.callsByType[`${R}qa-engineer`] ?? 0, 0, c.name)
      assert.ok(r.logs.some(l => /HALT implement-failed/.test(l)), c.name)
    })
  },
}
