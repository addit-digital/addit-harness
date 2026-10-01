import assert from 'node:assert/strict'

const R = 'addit-harness:'
let n = 0
export default {
  args: { slug: 's', track: 'backend', repo: '/r', planSha256: 'a'.repeat(64), tier: 'standard' },
  respond: ({ agentType }) => {
    if (agentType === `${R}qa-engineer`) return { passed: true, findings: [], evidence: [] }
    if (agentType.endsWith('code-reviewer') || agentType.startsWith('pr-review-toolkit:'))
      return { findings: [{ severity: 'blocking', description: `issue ${n++}` }] }
    return 'done'
  },
  expect: out => {
    assert.equal(out.error, null)
    assert.equal(out.result.clean, false)
    assert.equal(out.result.reviewRounds, 3)
    assert.equal(out.result.fixRounds, 2)
    assert.equal(out.result.reviewBreaker, false)
    assert.equal(out.result.haltedBy, null)
    assert.equal(out.callsByType[`${R}code-reviewer`], 3) // last pass is code-reviewer alone
    assert.equal(out.callsByType['pr-review-toolkit:pr-test-analyzer'], 2)
    assert.equal(out.callsByType[`${R}backend-developer`], 3) // implement + 2 fix rounds
    assert.equal(out.callsByType[`${R}qa-engineer`], 1) // QA still runs after a capped-out review loop
    assert.ok(out.logs.some(l => /did not reach clean/.test(l)))
  },
}
