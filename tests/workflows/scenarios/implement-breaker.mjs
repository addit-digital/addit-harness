import assert from 'node:assert/strict'

const R = 'addit-harness:'
export default {
  args: { slug: 's', track: 'backend', repo: '/r', planSha256: 'a'.repeat(64), tier: 'standard' },
  respond: ({ agentType }) => {
    if (agentType === `${R}qa-engineer`) return { passed: true, findings: [], evidence: [] }
    if (agentType === `${R}code-reviewer`) return { findings: [{ severity: 'blocking', description: 'same again' }] }
    if (agentType.startsWith('pr-review-toolkit:')) return null
    return 'done'
  },
  expect: out => {
    assert.equal(out.result.reviewBreaker, true)
    assert.equal(out.result.haltedBy, null) // non-convergence is not a halt
    assert.equal(out.result.clean, false)
    assert.equal(out.callsByType[`${R}qa-engineer`], 1) // QA still runs after the breaker
  },
}
