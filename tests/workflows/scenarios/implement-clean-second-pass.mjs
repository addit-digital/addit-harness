import assert from 'node:assert/strict'

const R = 'addit-harness:'
let reviewerPass = 0
export default {
  args: { slug: 's', track: 'backend', repo: '/r', planSha256: 'a'.repeat(64), tier: 'standard' },
  respond: ({ agentType }) => {
    if (agentType === `${R}qa-engineer`) return { passed: true, findings: [], evidence: [] }
    if (agentType === `${R}code-reviewer`) {
      return reviewerPass++ === 0 ? { findings: [{ severity: 'major', description: 'fix me' }] } : { findings: [] }
    }
    if (agentType.startsWith('pr-review-toolkit:')) return { findings: [] }
    return 'done'
  },
  expect: out => {
    assert.equal(out.result.clean, true)
    assert.equal(out.result.reviewRounds, 2)
    assert.equal(out.result.fixRounds, 1)
  },
}
