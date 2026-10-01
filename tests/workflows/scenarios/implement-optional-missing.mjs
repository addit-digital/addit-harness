import assert from 'node:assert/strict'

const R = 'addit-harness:'
export default {
  args: { slug: 's', track: 'backend', repo: '/r', planSha256: 'a'.repeat(64), tier: 'standard' },
  respond: ({ agentType }) => {
    if (agentType === `${R}qa-engineer`) return { passed: true, findings: [], evidence: [] }
    if (agentType === `${R}code-reviewer`) return { findings: [], touchedFiles: [{ repo: '/r', path: 'a.js' }] }
    if (agentType.startsWith('pr-review-toolkit:')) throw new Error('Unknown agent type: ' + agentType)
    return 'done'
  },
  expect: out => {
    assert.equal(out.result.clean, true)
    assert.equal(out.result.haltedBy, null)
    assert.deepEqual(out.logs, []) // absent optional reviewers are not an error
  },
}
