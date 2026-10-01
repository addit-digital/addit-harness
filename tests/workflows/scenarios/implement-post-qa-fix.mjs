import assert from 'node:assert/strict'

const R = 'addit-harness:'
const CASES = [
  { tier: 'light', qa: [false, true] },
  { tier: 'standard', qa: [false, true] },
  { tier: 'standard', qa: [false, false] },
]
const qaSeen = [0, 0, 0]
export default {
  argsList: CASES.map(c => ({ slug: 's', track: 'backend', repo: '/r', planSha256: 'a'.repeat(64), tier: c.tier })),
  respond: ({ agentType }, state) => {
    if (agentType === `${R}qa-engineer`) return { passed: CASES[state.run].qa[qaSeen[state.run]++], findings: ['x'], evidence: [] }
    if (agentType.endsWith('code-reviewer') || agentType.startsWith('pr-review-toolkit:')) return { findings: [], touchedFiles: [{ repo: '/r', path: 'a.js' }] }
    return 'done'
  },
  expect: ({ runs }) => {
    const [light, standard, stuck] = runs
    assert.equal(light.result.qaPassed, true)
    assert.equal(light.result.qaRuns, 2)
    assert.equal(light.result.postQaFixRan, true)
    assert.equal(light.result.postQaFixReviewed, false) // light: disclosed, not reviewed
    assert.ok(light.logs.includes('Post-QA fix was not code-reviewed (light tier)'))
    assert.equal(light.callsByType[`${R}code-reviewer`], 1) // only the review loop's pass
    assert.equal(standard.result.postQaFixReviewed, true)
    assert.equal(standard.callsByType[`${R}code-reviewer`], 2) // review loop + scoped re-review of the QA fix
    assert.equal(stuck.result.qaPassed, false)
    assert.equal(stuck.callsByType[`${R}qa-engineer`], 2) // never a third QA run
    assert.deepEqual(stuck.phases, ['Implement', 'Review', 'QA', 'QA fix'])
  },
}
