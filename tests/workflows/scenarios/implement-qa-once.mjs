import assert from 'node:assert/strict'

const R = 'addit-harness:'
const TIERS = ['light', 'standard', 'deep']
export default {
  argsList: TIERS.map(tier => ({ slug: 's', track: 'backend', repo: '/r', planSha256: 'a'.repeat(64), tier })),
  respond: ({ agentType }) => {
    if (agentType === `${R}qa-engineer`) return { passed: true, findings: [], evidence: [] }
    if (agentType.endsWith('code-reviewer') || agentType.startsWith('pr-review-toolkit:')) return { findings: [], touchedFiles: [] }
    return 'done'
  },
  expect: ({ runs }) => {
    runs.forEach((r, i) => {
      assert.equal(r.callsByType[`${R}qa-engineer`], 1, TIERS[i]) // clean review + passing QA: exactly one QA call
      assert.equal(r.result.clean, true, TIERS[i])
      assert.equal(r.result.qaPassed, true, TIERS[i])
      assert.equal(r.result.postQaFixRan, false, TIERS[i])
    })
    assert.deepEqual(runs.map(r => r.calls), [3, 7, 7]) // light: implement + 1 reviewer + QA; else + 5 reviewers
    assert.equal(runs[0].callsByType[`${R}code-reviewer`], 1)
    assert.equal(runs[0].callList[1].opts.effort, 'low')
    assert.equal(runs[2].callList[1].opts.effort, 'high')
  },
}
